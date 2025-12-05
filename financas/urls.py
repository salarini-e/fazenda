from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
 
app_name='financas'
urlpatterns = [
    path('', views.index, name='home'),    
    path('nfs-e/', views.nfse, name='nfse'), 
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
