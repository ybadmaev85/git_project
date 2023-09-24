from blog.forms import ArticleForm
from blog.models import Article

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from mailings.services import get_articles_from_cache

from typing import Any


class ArticleListView(ListView):
    '''
    Класс для отображения всех статей блога
    '''
    model = Article

    def get_queryset(self) -> QuerySet:
        return get_articles_from_cache()

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Блог'

        return context


class ArticleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    Класс для отображения одной статьи блога
    '''
    model = Article
    permission_required = 'blog.view_article'

    def get_object(self, queryset=None) -> Article:
        self.object = super().get_object(queryset)
        self.object.view_count += 1
        self.object.save()

        return self.object

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.title}'

        return context


class ArticleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    '''
    Класс для создания статьи блога
    '''
    model = Article
    permission_required = 'blog.add_article'
    form_class = ArticleForm
    success_url = reverse_lazy('blog:article_list')

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание статьи'

        return context


class ArticleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    Класс для обновления статьи блога
    '''
    model = Article
    permission_required = 'blog.change_article'
    form_class = ArticleForm
    success_url = reverse_lazy('blog:article_list')

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление статьи {self.object.title}'

        return context


class ArticleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    '''
    Класс для удаления статьи блога
    '''
    model = Article
    permission_required = 'blog.delete_article'
    success_url = reverse_lazy('blog:article_list')

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление статьи {self.object.title}'

        return context
