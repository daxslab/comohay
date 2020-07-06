import subprocess

from celery import shared_task


@shared_task
def crawl():
    # using subprocess.Popen instead of call_command because of celery issues with multiprocessing
    subprocess.Popen(['python', 'manage.py', 'proxy_crawler'])
    subprocess.Popen(['python', 'manage.py', 'crawl'])
    subprocess.Popen(['python', 'manage.py', 'remove_duplicated_ads'])
