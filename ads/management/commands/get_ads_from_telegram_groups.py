import datetime
import re
import ads.services.ad_service
import currencies.services.currencyad_service
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from telethon import TelegramClient
from ads.models import TelegramGroup, Ad
import logging
import comohay.settings
from currencies.services import currencyad_service
import asyncio

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    base_datetime = datetime.datetime(2020, 8, 1, tzinfo=datetime.timezone.utc)
    minutes_offset = 20

    help = "Get messages from all telegram groups saved in db. By default will only be fetch the messages in the " \
           "last 10 minutes per each group. If you add \"--all-messages\" option all messages will be fetched. If you" \
           "add --groups <group-username> only the ads of the group will be fetched"

    lock = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Telegram desktop sample keys, see https://docs.telethon.dev/en/latest/basic/signing-in.html
        self.client = TelegramClient('anon', comohay.settings.TELEGRAM_API_ID, comohay.settings.TELEGRAM_API_HASH)

    def add_arguments(self, parser):

        parser.add_argument('--groups', nargs='+', type=str)

        parser.add_argument('--minutes-offset', type=int)

        parser.add_argument(
            '--all-messages',
            action='store_true',
            help='Process all messages from the selected groups since 2020-08-01',
        )

    def handle(self, *args, **options):

        if options['minutes_offset']:
            self.minutes_offset = options['minutes_offset']

        if options['all_messages']:
            offset_datetime = self.base_datetime
        else:
            offset_datetime = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(
                minutes=self.minutes_offset)

        if options['groups']:
            tg_groups = list(TelegramGroup.objects.filter(username__in=options['groups']))
        else:
            tg_groups = list(TelegramGroup.objects.all())

        print("Fetching telegram messages ...")

        async def main():
            await asyncio.gather(*[self.process_group(telegram_group, offset_datetime) for telegram_group in tg_groups])

        with self.client:
            try:
                self.client.loop.run_until_complete(main())
            except Exception as e:
                logger.error(e)

    async def process_group(self, telegram_group: TelegramGroup, offset_datetime: datetime):
        try:

            async for message in self.client.iter_messages(
                    entity="@{}".format(telegram_group.username),
                    offset_date=offset_datetime,
                    reverse=True,
                    wait_time=5
            ):

                await message.get_sender()

                if message.text is None or \
                        message.sender is None or \
                        message.sender.deleted or \
                        message.sender.bot or \
                        message.sender.scam or \
                        message.sender.fake or \
                        not message.sender.username:
                    continue

                # TODO:
                #  Here must go a more general classifier.
                #  Right now we only accept ads that match the regex for a currencyad
                matches = re.match(currencies.services.currencyad_service.regex, message.text, re.IGNORECASE)
                if not matches:
                    continue

                ad = Ad(
                    title=matches.group(0),
                    category_id=87,  # id of category "Cambio de Moneda"
                    description=message.text,
                    province_id=telegram_group.province_id,
                    contact_tg=message.sender.username,
                    external_source="t.me/{group_username}".format(group_username=telegram_group.username),
                    external_id=message.id,
                    external_url=telegram_group.link + "/{id}".format(id=message.id),
                    external_created_at=message.date,
                    is_deleted=False
                )

                # locking while detecting duplicates and saving the ad, this way we avoid the appearance of duplicates
                # when two similar ads are processing concurrently
                while self.lock:
                    await asyncio.sleep(0.1)
                self.lock = True

                currencyad = currencies.services.currencyad_service.get_currencyad_from_ad(ad)
                if currencyad:

                    if await sync_to_async(Ad.objects.filter(external_url=ad.external_url).count)() > 0 or \
                            await sync_to_async(currencyad_service.get_newest_similar_currencyads(currencyad).count)() > 0:
                        self.lock = False
                        continue

                    await sync_to_async(currencyad_service.soft_delete_older_similar_currencyads)(currencyad)

                    ad.currency_iso = currencyad.target_currency_iso
                    ad.price = currencyad.price
                    await sync_to_async(ad.save)()
                    await sync_to_async(currencyad.save)()

                    logger.info(
                        "New Ad from Telegram message: {}, {}, {}, {}".format(
                            message.date,
                            telegram_group.username,
                            message.sender.username,
                            message.text,
                        )
                    )

                    logger.info(
                        "New CurrencyAd from Telegram message: {}/{} {}".format(
                            currencyad.source_currency_iso,
                            currencyad.target_currency_iso,
                            currencyad.price
                        )
                    )

                else:
                    # right now this is not reachable because the classifier only detect currencyads
                    if await sync_to_async(ads.services.ad_service.has_duplicates)(ad):
                        # TODO: do something similar as in BaseAdPipeline
                        self.lock = False
                        continue

                    await sync_to_async(ad.save)()

                    logger.info(
                        "New Ad from Telegram message: {}, {}, {}, {}".format(
                            message.date,
                            telegram_group.username,
                            message.sender.username,
                            message.text,
                        )
                    )

                # unlocking db
                self.lock = False

        except Exception as e:
            logger.error(e)
