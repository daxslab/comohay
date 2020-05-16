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
                target=TelegramBot.send_photo if ad.adimage_set.count() > 0 else TelegramBot.send_message,
                args=(updater.bot, group, ad, request)
            )
            thread.start()
            threads.append(thread)

        if ad.province:
            for group in settings.TELEGRAM_BOT_GROUPS[ad.province.name]:
                thread = Thread(
                    target=TelegramBot.send_photo if ad.adimage_set.count() > 0 else TelegramBot.send_message,
                    args=(updater.bot, group, ad, request, True)
                )
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()

    @staticmethod
    def send_message(bot, group, ad, request, provincial=False):
        message = TelegramBot.get_ad_provincial_message(ad) if provincial else TelegramBot.get_ad_national_message(ad)
        bot.sendMessage(
            chat_id='@{}'.format(group),
            text="<a href=\"{}\">{}</a>".format(request.build_absolute_uri(ad.get_absolute_url()),
                                                message),
            parse_mode='HTML'
        )

    @staticmethod
    def send_photo(bot, group, ad, request, provincial=False):
        message = TelegramBot.get_ad_provincial_message(ad) if provincial else TelegramBot.get_ad_national_message(ad)
        # bot.sendPhoto('@{}'.format(group), request.build_absolute_uri(ad.adimage_set.first().image.url), ad.title)
        bot.sendPhoto(
            chat_id='@{}'.format(group),
            photo=open('{}{}'.format(settings.BASE_DIR, ad.adimage_set.first().image.url), 'rb'),
            caption="{}\n{}".format(message, request.build_absolute_uri(ad.get_absolute_url())),
            parse_mode='HTML'
        )

    @staticmethod
    def get_ad_national_message(ad):
        if ad.province and ad.municipality:
            return "{} ({}. {}, {})".format(ad.title, ad.price, ad.municipality, ad.province)
        elif ad.province:
            return "{} ({}. {})".format(ad.title, ad.price, ad.province)

        return "{} ({})".format(ad.title, ad.price)

    @staticmethod
    def get_ad_provincial_message(ad):
        if ad.municipality:
            return "{} ({}. {})".format(ad.title, ad.price, ad.municipality)

        return "{} ({})".format(ad.title, ad.price)
