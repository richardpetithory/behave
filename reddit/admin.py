from django.contrib import admin
from django.contrib.auth.models import Group, User
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

    save_as = True


class SubredditAdmin(admin.ModelAdmin):
    pass


class AuthorizedUserAdmin(admin.ModelAdmin):
    form = AuthorizedUserForm


class RemovedPostAdmin(admin.ModelAdmin):
    list_display = ('post_title', 'author_search_link', 'removal_date', 'removal_action', 'post_title_link')
    search_fields = ('author', 'post_title')
    list_filter = ('subreddit__display_name', 'removal_action', 'removal_date')

    def post_title_link(self, post):
        return format_html('<a href="{url}">link</a>'.format(url=post.post_url))
    post_title_link.allow_tags = True
    post_title_link.short_description = "Post URL"

    def author_search_link(self, post):
        return format_html('<a href="?q={author}">{author}</a>'.format(author=post.author))
    author_search_link.allow_tags = True
    author_search_link.short_description = "Author"
    author_search_link.admin_order_field = "author"


admin.site.register(Subreddit, SubredditAdmin)
admin.site.register(AuthorizedUser, AuthorizedUserAdmin)
admin.site.register(RemovedPost, RemovedPostAdmin)
admin.site.register(RemovalAction, RemovalActionAdmin)

admin.site.unregister(Group)
admin.site.unregister(User)

admin.site.site_header = "Behave Bot Administration"
admin.site.site_title = "Behave Bot"
admin.site.index_title = ""
