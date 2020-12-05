from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from reddit.models import (
    AuthorizedUser,
    AuthorizedUserForm,
    RemovalAction,
    RemovedPost,
    Subreddit,
)


class RemovalActionAdmin(admin.ModelAdmin):
    list_display = ('subreddit', 'flair_text', 'description', 'ban_duration', 'permanent_ban', 'lock_post')
    ordering = ('subreddit', 'flair_text')


class SubredditAdmin(admin.ModelAdmin):
    pass


class AuthorizedUserAdmin(admin.ModelAdmin):
    form = AuthorizedUserForm


class RemovedPostAdmin(admin.ModelAdmin):
    list_display = ('post_title', 'author', 'removal_date', 'post_url_link')

    def post_url_link(self, post):
        return format_html('<a href="{url}">{url}</a>'.format(url=post.post_url))

    post_url_link.allow_tags = True
    post_url_link.short_description = "Post URL"


admin.site.register(Subreddit, SubredditAdmin)
admin.site.register(AuthorizedUser, AuthorizedUserAdmin)
admin.site.register(RemovedPost, RemovedPostAdmin)
admin.site.register(RemovalAction, RemovalActionAdmin)

admin.site.unregister(Group)
