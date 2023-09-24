from blog.models import Article

from django.contrib import admin


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'view_count', 'publish_date',)
    search_fields = ('title', 'body',)
    ordering = ('-publish_date',)
