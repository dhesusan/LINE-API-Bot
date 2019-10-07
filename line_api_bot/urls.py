from django.urls import path, include

urlpatterns = [
    path('callback/', include('top_api.urls')),
]
