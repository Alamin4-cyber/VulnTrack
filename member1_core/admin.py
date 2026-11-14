from django.contrib import admin
from .models import UserProfile, Target
from .models import Subdomain, DNSRecord

admin.site.register(UserProfile)
admin.site.register(Target)

admin.site.register(Subdomain)  
admin.site.register(DNSRecord)