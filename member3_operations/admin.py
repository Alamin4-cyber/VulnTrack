from django.contrib import admin
from .models import ScanJob, ScanLog, Evidence, Remediation, Notification, Report

admin.site.register(ScanJob)
admin.site.register(ScanLog)
admin.site.register(Evidence)
admin.site.register(Remediation)
admin.site.register(Notification)
admin.site.register(Report)
