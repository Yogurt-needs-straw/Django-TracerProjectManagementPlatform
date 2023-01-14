from django.contrib import admin
from django.urls import path

from app01 import views

urlpatterns = [
    path('send/sms/', views.send_sms),
    path('register/', views.register),

]
