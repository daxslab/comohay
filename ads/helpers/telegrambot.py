from django.conf import settings
from telegram.ext import Updater
from ads.tasks import send_telegram_message


class TelegramBot:

    @staticmethod
    def broadcast_ad(ad):
        for group in settings.TELEGRAM_BOT_GROUPS['NATIONAL_WIDE']:
            TelegramBot.send_ad_message(group, ad)

        if ad.province:
            for group in settings.TELEGRAM_BOT_GROUPS[ad.province.name]:
                TelegramBot.send_ad_message(group, ad, False)

    @staticmethod
    def send_ad_message(chat_id, ad, show_province=True):
        # todo: check the html markup here with images, as far as I remember the html with images didn't work
        if ad.adimage_set.count() > 0:
            photo = open('{}{}'.format(settings.BASE_DIR, ad.adimage_set.first().image.url), 'rb')
            # photo = request.build_absolute_uri(ad.adimage_set.first().image.url)
            send_telegram_message.apply_async((chat_id, TelegramBot.get_ad_message(ad, show_province), photo),
                                              retry=True)
        else:
            send_telegram_message.apply_async((chat_id, TelegramBot.get_ad_message(ad, show_province)), retry=True)

    @staticmethod
    def send_message(chat_id, message, photo=None, parse_mode='HTML'):
        bot = Updater(settings.TELEGRAM_BOT_TOKEN, use_context=True).bot
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
    def get_ad_message(ad, show_province=True):
        message = ''

        if show_province:
            if ad.province and ad.municipality:
                message += "{}, {}\n".format(ad.province, ad.municipality)
            elif ad.province:
                message += "{}\n".format(ad.province)
        elif ad.municipality:
            message += "{}\n".format(ad.municipality)

        if ad.price > 0:
            message += "<b>{} {}</b> - <a href=\"{}\">{}</a>".format(ad.get_user_price(), ad.user_currency,
                                                              ad.get_url_with_redirection(absolute=True), ad.title)
        else:
            message += "<a href=\"{}\">{}</a>".format(ad.get_url_with_redirection(absolute=True), ad.title)

        message += "\n<code>{}</code>".format(ad.external_source)

        return message
