from django.contrib import admin
from django.urls import path
from . import views
 
app_name='financas'
urlpatterns = [
    path('', views.index, name='home'),    
    path('nfs-e/', views.nfse, name='nfse'), 
]