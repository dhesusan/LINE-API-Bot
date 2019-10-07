from django.urls import path, include

urlpatterns = [
    path('callback/', include('bot.urls')),
]
