from blog.apps import BlogConfig
from blog.views import (
    ArticleListView, ArticleDetailView, ArticleCreateView, ArticleUpdateView, ArticleDeleteView
)

from django.urls import path

app_name = BlogConfig.name

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('create_article/', ArticleCreateView.as_view(), name='article_create'),
    path('update_article/<int:pk>/', ArticleUpdateView.as_view(), name='article_update'),
    path('delete_article/<int:pk>/', ArticleDeleteView.as_view(), name='article_delete'),
]
