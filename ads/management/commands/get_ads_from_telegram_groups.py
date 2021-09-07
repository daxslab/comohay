import datetime
import re
import ads.services.ad_service
import currencies.services.currencyad_service
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from telethon import TelegramClient
from ads.models import TelegramGroup, Ad


class Command(BaseCommand):
    base_datetime = datetime.datetime(2020, 8, 1, tzinfo=datetime.timezone.utc)
    minutes_offset = 20

    help = "Get messages from all telegram groups saved in db. By default will only be fetch the messages in the " \
           "last 10 minutes per each group. If you add \"--all-messages\" option all messages will be fetched. If you" \
           "add --groups <group-username> only the ads of the group will be fetched"

    def add_arguments(self, parser):

        parser.add_argument('--groups', nargs='+', type=str)

        parser.add_argument('--minutes-offset', type=int)

        parser.add_argument(
            '--all-messages',
            action='store_true',
            help='Process all messages from the selected groups since 2020-08-01',
        )

    def handle(self, *args, **options):
        # Telegram desktop sample keys, see https://docs.telethon.dev/en/latest/basic/signing-in.html
        api_id = 7589070
        api_hash = '49b83716f931e62c113b9b88f95ae1b9'
        client = TelegramClient('anon', api_id, api_hash)

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

            # tg_groups = await sync_to_async(list)(TelegramGroup.objects.all())
            for telegram_group in tg_groups:
                async for message in client.iter_messages(
                        entity="@{}".format(telegram_group.username),
                        offset_date=offset_datetime,
                        reverse=True,
                        wait_time=5
                ):

                    await message.get_sender()

                    if message.text is None or message.sender is None or message.sender.deleted or message.sender.bot or message.sender.scam or message.sender.fake:
                        continue

                    # TODO: Here must go a more general classifier. Right now
                    # we only accept ads that match the regex for a currency
                    # exchange ad
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

                    if await sync_to_async(ads.services.ad_service.has_duplicates)(ad, verbose=True):
                        continue

                    await sync_to_async(ad.save)()

                    print("New Ad from Telegram message: ", message.date, telegram_group.username, message.text)

                    currencyad = currencies.services.currencyad_service.get_currencyad_from_ad(ad)
                    if currencyad:
                        ad.currency_iso = currencyad.target_currency_iso
                        ad.price = currencyad.price
                        await sync_to_async(ad.save)()
                        await sync_to_async(currencyad.save)()
                        print("New CurrencyAd from Telegram message: ", currencyad.source_currency_iso,
                              currencyad.target_currency_iso, currencyad.price)

        with client:
            client.loop.run_until_complete(main())
