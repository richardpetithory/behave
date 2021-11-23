from django.contrib import admin
from django.urls import path

from reddit.views import authenticate, oauth_callback, user_pushshift_history

urlpatterns = [
    path('user/<slug:username>', user_pushshift_history),
    path('authenticate', authenticate),
    path('oauth', oauth_callback),
    path('', admin.site.urls),
    ]
