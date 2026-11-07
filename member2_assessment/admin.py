from django.contrib import admin
from .models import ScanProfile, ScopeRule

admin.site.register(ScanProfile)
admin.site.register(ScopeRule)