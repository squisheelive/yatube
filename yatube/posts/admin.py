from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostGroup(admin.ModelAdmin):
    list_display = ("title", "slug", "description")
    empty_value_display = "-пусто-"


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group", "image")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author")
    list_filter = ("user", "author")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("created", "text", "author", "post")
    list_filter = ("author",)


admin.site.register(Follow, FollowAdmin)
admin.site.register(Group, PostGroup)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
