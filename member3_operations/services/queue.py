from django.conf import settings


def enqueue_scan(scan_id):
    if getattr(settings, "USE_CELERY", False):
        from member3_operations.tasks import run_scan_task
        run_scan_task.delay(scan_id)
    else:
        from member3_operations.services.scanner import execute_scan
        execute_scan(scan_id)
