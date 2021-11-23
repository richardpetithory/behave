import requests
import datetime

from logging import getLogger

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from reddit import get_base_reddit_connection
from reddit.models import AuthorizedUser

log = getLogger(__name__)


@login_required
def authenticate(request):
    reddit = get_base_reddit_connection()

    return redirect(reddit.auth.url(["identity"], "...", "permanent"))


@login_required
def oauth_callback(request):
    reddit = get_base_reddit_connection()

    refresh_token = str(reddit.auth.authorize(request.GET.get('code')))
    username = str(reddit.user.me())

    search_from = datetime.datetime.utcnow()

    authorized_user, _ = AuthorizedUser.objects.get_or_create(
        username=username,
        defaults={
            'username': username,
        }
    )

    authorized_user.refresh_token = refresh_token

    authorized_user.save()

    return redirect("/reddit/authorizeduser/")


def user_pushshift_history(request, username):
    search_to = datetime.datetime.utcnow()
    search_from = search_to - datetime.timedelta(days=365*20)

    query_url_template = "https://api.pushshift.io/reddit/search/comment/?" \
                         "q=&" \
                         "size=100&" \
                         "sort=desc&" \
                         "sort_type=created_utc&" \
                         "after={search_from}&" \
                         "before={search_to}&" \
                         "subreddit=&" \
                         "author={username}&" \
                         "aggs=link_id"

    query_url = query_url_template.format(
        username=username,
        search_from=str(round(search_from.timestamp())),
        search_to=str(round(search_to.timestamp()))
    )

    try:
        user_activity = requests.get(query_url)

        user_activity = user_activity.json()

        if 'data' not in user_activity:
            return HttpResponse("malformed response")

        context = {
            'user_activity': user_activity['data']
        }

        return render(request, 'user_pushshift_history.html', context=context)
    except requests.RequestException as e:
        return HttpResponse(e)
    except Exception as e:
        return HttpResponse(e)
