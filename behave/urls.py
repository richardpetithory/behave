from django.contrib import admin
from django.urls import path

from reddit.views import authenticate, oauth_callback

urlpatterns = [
    path('authenticate', authenticate),
    path('oauth', oauth_callback),
    path('', admin.site.urls),
    ]
