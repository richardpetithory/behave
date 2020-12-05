from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from reddit import get_base_reddit_connection
from reddit.models import AuthorizedUser


@login_required
def authenticate(request):
    reddit = get_base_reddit_connection()

    return redirect(reddit.auth.url(["identity"], "...", "permanent"))


@login_required
def oauth_callback(request):
    reddit = get_base_reddit_connection()

    refresh_token = str(reddit.auth.authorize(request.GET.get('code')))
    username = str(reddit.user.me())

    authorized_user, _ = AuthorizedUser.objects.get_or_create(
        username=username,
        defaults={
            'username': username,
        }
    )

    authorized_user.refresh_token = refresh_token

    authorized_user.save()

    return redirect("/reddit/authorizeduser/")
