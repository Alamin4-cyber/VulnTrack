from celery import shared_task
from .services.scanner import execute_scan


@shared_task
def run_scan_task(scan_id):
    execute_scan(scan_id)
