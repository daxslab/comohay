import subprocess

from celery import shared_task


@shared_task
def crawl():
    # using subprocess.Popen instead of call_command because of celery issues with multiprocessing
    subprocess.Popen(['python', 'manage.py', 'proxy_crawler'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.Popen(['python', 'manage.py', 'crawl'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
