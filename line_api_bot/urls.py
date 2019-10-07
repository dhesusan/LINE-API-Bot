from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('callback/', include('bot.urls')),
    path('admin/', admin.site.urls),
    path('callback/', include('bot.urls')),
]
