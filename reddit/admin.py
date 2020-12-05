from django.contrib import admin
from django.utils.html import format_html

from reddit.models import AuthorizedUser, Subreddit, RemovalAction, RemovedPost


class RemovalActionAdmin(admin.ModelAdmin):
    list_display = ('subreddit', 'flair_text', 'description', 'ban_duration')


class RemovalActionInlineAdmin(admin.StackedInline):
    model = RemovalAction

    def get_extra(self, request, obj=None, **kwargs):
        return 0


class SubredditAdmin(admin.ModelAdmin):
    inlines = [
        RemovalActionInlineAdmin,
    ]


class AuthorizedUserAdmin(admin.ModelAdmin):
    pass
    # readonly_fields = ('username', )
    # exclude = ('password', 'refresh_token')


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
