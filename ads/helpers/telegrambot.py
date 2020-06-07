from django.conf import settings
from telegram.ext import Updater
from threading import Thread


class TelegramBot:

    @staticmethod
    def broadcast_ad(ad, request):
        updater = Updater(settings.TELEGRAM_BOT_TOKEN, use_context=True)

        threads = []

        for group in settings.TELEGRAM_BOT_GROUPS['NATIONAL_WIDE']:
            thread = Thread(
                target=TelegramBot.send_ad_photo if ad.adimage_set.count() > 0 else TelegramBot.send_ad_message,
                args=(updater.bot, group, ad, request)
            )
            thread.start()
            threads.append(thread)

        if ad.province:
            for group in settings.TELEGRAM_BOT_GROUPS[ad.province.name]:
                thread = Thread(
                    target=TelegramBot.send_ad_photo if ad.adimage_set.count() > 0 else TelegramBot.send_ad_message,
                    args=(updater.bot, group, ad, request, True)
                )
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()

    @staticmethod
    def send_ad_message(bot, chat_id, ad, request, provincial=False):
        raw_message = TelegramBot.get_ad_provincial_message(ad) if provincial else TelegramBot.get_ad_national_message(
            ad)
        message = "<a href=\"{}\">{}</a>".format(request.build_absolute_uri(ad.get_absolute_url()), raw_message)
        TelegramBot.send_message(bot, chat_id, message)

    @staticmethod
    def send_ad_photo(bot, chat_id, ad, request, provincial=False):
        raw_message = TelegramBot.get_ad_provincial_message(ad) if provincial else TelegramBot.get_ad_national_message(
            ad)
        message = "{}\n{}".format(raw_message, request.build_absolute_uri(ad.get_absolute_url()))
        photo = open('{}{}'.format(settings.BASE_DIR, ad.adimage_set.first().image.url), 'rb')
        # photo = request.build_absolute_uri(ad.adimage_set.first().image.url)
        TelegramBot.send_message(bot, chat_id, message, photo)

    @staticmethod
    def send_message(bot, chat_id, message, photo=None, parse_mode='HTML'):
        if not photo:
            bot.sendMessage(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
        else:
            bot.sendPhoto(
                chat_id=chat_id,
                photo=photo,
                caption=message,
                parse_mode=parse_mode
            )

    @staticmethod
    def get_ad_national_message(ad):
        if ad.province and ad.municipality:
            return "{} ({} {}. {}, {})".format(ad.title, ad.get_user_price(), ad.user_currency, ad.municipality, ad.province)
        elif ad.province:
            return "{} ({} {}. {})".format(ad.title, ad.get_user_price(), ad.user_currency, ad.province)

        return "{} ({} {})".format(ad.title, ad.get_user_price(), ad.user_currency)

    @staticmethod
    def get_ad_provincial_message(ad):
        if ad.municipality:
            return "{} ({} {}. {})".format(ad.title, ad.get_user_price(), ad.user_currency, ad.municipality)

        return "{} ({} {})".format(ad.title, ad.get_user_price(), ad.user_currency)
