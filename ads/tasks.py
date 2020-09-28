from celery import shared_task
from django.core.management import call_command


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
