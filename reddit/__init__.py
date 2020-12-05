import praw

from behave import settings


def get_base_reddit_connection():
    return praw.Reddit(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        redirect_uri=settings.REDIRECT_URI,
        user_agent=settings.DEFAUT_USER_AGENT
    )


def get_authed_reddit_connection(access_user):
    kwargs = dict(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        user_agent=settings.DEFAUT_USER_AGENT
    )

    if access_user.username and access_user.password:
        kwargs['username'] = access_user.username
        kwargs['password'] = access_user.password
    else:
        kwargs['refresh_token'] = access_user.refresh_token

    return praw.Reddit(**kwargs)
