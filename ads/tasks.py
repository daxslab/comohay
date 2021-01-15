from celery import shared_task
from django.core.management import call_command
from ads.models import Ad


@shared_task
def update_index():
    call_command('update_index')


@shared_task
def get_proxies():
    call_command('proxy_crawler')


@shared_task
def crawl():
    call_command('crawl', '--depth', '10')


@shared_task
def crawl_revolico():
    call_command('crawl', 'revolico', '--depth', '4')


@shared_task
def updater():
    call_command('crawl', 'updater')


@shared_task
def broadcast_in_telegram(ad_id: int):
    from ads.helpers.telegrambot import TelegramBot
    try:
        ad = Ad.objects.get(id=ad_id)
        TelegramBot.broadcast_ad(ad)
    except Ad.DoesNotExist:
        pass


@shared_task(rate_limit='10/m')
def send_telegram_message(chat_id, message, photo=None, parse_mode='HTML'):
    from ads.helpers.telegrambot import TelegramBot
    TelegramBot.send_message(chat_id, message, photo, parse_mode)


@shared_task
def clean_lazy_users():
    call_command('clean_lazy_users')
