from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # 👇 Member 3 must be first because it owns the root "/" (Dashboard) and "/scans/"
    path("", include("member3_operations.urls")),              
    
    # 👇 Member 1 handles "/targets/", "/accounts/", etc.
    path("", include("member1_core.urls")),                    
    
    # 👇 Member 2 handles "/assessment/"
    path("assessment/", include("member2_assessment.urls")),   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)