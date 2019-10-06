from . import views
from django.urls import path

app_name = 'top_api'

urlpatterns = [
    path('', views.callback, name='callback'),
]