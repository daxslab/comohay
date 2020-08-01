import subprocess

from celery import shared_task


@shared_task
def update_index():
    subprocess.Popen(['python', 'manage.py', 'update_index'])


@shared_task
def updater():
    subprocess.Popen(['python', 'manage.py', 'updater'])


@shared_task
def crawl():
    # using subprocess.Popen instead of call_command because of celery issues with multiprocessing
    subprocess.Popen(['python', 'manage.py', 'proxy_crawler'])
    subprocess.Popen(['python', 'manage.py', 'crawl'])
