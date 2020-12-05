import praw
from django.db import models

from reddit import get_authed_reddit_connection


class AuthorizedUser(models.Model):
    username = models.CharField(
        unique=True,
        max_length=20,
        default="",
        null=False,
        blank=False
    )

    password = models.CharField(
        max_length=100,
        default="",
        blank=True,
        null=False
    )

    refresh_token = models.CharField(
        max_length=100,
        default="",
        blank=True,
        null=False
    )

    def __str__(self):
        return self.username


class Subreddit(models.Model):
    access_user = models.ForeignKey(
        to=AuthorizedUser,
        on_delete=models.DO_NOTHING
    )

    display_name = models.CharField(
        max_length=21,
        null=False,
        blank=False
    )

    active = models.BooleanField(
        default=True,
        null=False
    )

    default_ban_message = models.TextField(
        default="",
        blank=True,
        null=False
    )

    def __str__(self):
        return self.display_name

    @property
    def reddit_api(self) -> praw.Reddit:
        return get_authed_reddit_connection(self.access_user)

    @property
    def api(self) -> praw.reddit.Subreddit:
        return self.reddit_api.subreddit(self.display_name)


class RemovalAction(models.Model):
    subreddit = models.ForeignKey(
        to="Subreddit",
        on_delete=models.CASCADE
    )

    flair_text = models.CharField(
        max_length=200,
        db_index=True,
        default="",
        blank=False,
        null=False
    )

    description = models.CharField(
        max_length=200,
        default="",
        blank=True,
        null=False
    )

    comment_reply = models.TextField(
        default="",
        blank=True,
        null=False
    )

    ban_duration = models.IntegerField(
        default=0,
        null=False
    )

    ban_reason = models.CharField(
        max_length=100,
        default="",
        blank=True,
        null=False
    )

    use_default_ban_message = models.BooleanField(
        default=True,
        null=False
    )

    ban_message = models.TextField(
        default="",
        blank=True,
        null=False
    )

    ban_note = models.CharField(
        max_length=200,
        default="{0.shortlink}",
        blank=True,
        null=False
    )

    lock_post = models.BooleanField(
        default=False,
        null=False
    )


class RemovedPost(models.Model):
    subreddit = models.ForeignKey(
        to=Subreddit,
        on_delete=models.CASCADE
    )

    removal_date = models.DateTimeField(
        auto_created=True,
        null=True
    )

    author = models.CharField(
        max_length=20,
        default="",
        null=False,
        blank=False
    )

    submission_id = models.CharField(
        max_length=20,
        unique=True,
        default="",
        blank=False,
        null=False
    )

    flair_text_set = models.CharField(
        max_length=200,
        default=None,
        blank=True,
        null=True
    )

    removal_comment_id = models.CharField(
        max_length=20,
        default=None,
        blank=True,
        null=True
    )

    post_title = models.CharField(
        max_length=1024,
        default="",
        blank=False,
        null=False
    )

    post_url = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        null=False
    )

    def __str__(self):
        return self.post_title
