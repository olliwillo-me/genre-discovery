from django.contrib import admin
from .models import Tag, Cloudcast


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'tag_type')
    list_filter = ('tag_type',)


@admin.register(Cloudcast)
class CloudcastAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'quality_score', 'play_count', 'publish_date', 'is_public')
    list_filter = ('is_public', 'tags')
    filter_horizontal = ('tags', 'listeners')
