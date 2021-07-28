from django.contrib import admin

from .models import Group, Post

# Отсортировано с помощью isort


class PostGroup(admin.ModelAdmin):
    list_display = ("title", "slug", "description")
    empty_value_display = "-пусто-"


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


admin.site.register(Group, PostGroup)
admin.site.register(Post, PostAdmin)
