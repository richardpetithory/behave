from django.contrib import admin
from django.urls import path

from reddit.views import authenticate, oauth_callback

urlpatterns = [
    path('admin/', admin.site.urls),

    path('authenticate', authenticate),
    path('oauth', oauth_callback),
]
