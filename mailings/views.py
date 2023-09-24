import random

from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
)
from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
)

from typing import Any

from pytils.translit import slugify

from mailings.forms import ClientForm, MailingForm
from mailings.models import Client, Mailing, MailingLogs, MailingStatus
from mailings.services import (
    check_mailing_status, check_user, get_articles_from_cache, get_status_object
)


class IndexView(TemplateView):
    '''
    Класс отображения главной страницы сервиса
    '''
    template_name = 'mailings/index.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        context['total_mailings'] = len(Mailing.objects.all())
        context['active_mailings'] = len(Mailing.objects.exclude(status=get_status_object('завершена')))
        context['unique_clients'] = len(Client.objects.values('email').distinct())
        try:
            context['blog_articles'] = random.sample(list(get_articles_from_cache()), 3)
        except ValueError:
            context['blog_articles'] = []

        return context


class MailingListView(LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin, ListView):
    '''
    Класс отображения страницы со всеми рассылками
    '''
    model = Mailing
    permission_required = 'mailings.view_mailing'

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(user=self.request.user)

        return queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Рассылки'

        return context

    def test_func(self) -> bool:
        return self.request.user.groups.filter(name='service_users')


class MailingDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    Класс для отображения информации об одной рассылке
    '''
    model = Mailing
    permission_required = 'mailings.view_mailing'

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        group = self.request.user.groups.filter(name='manager')
        status = self.get_object().status

        if not group:
            if not check_user(self.get_object().user, self.request.user):
                return redirect('mailings:mailing_list')
        else:
            if status == get_status_object('завершена'):
                return redirect('mailings:manager_mailing_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title

        return context


class MailingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    '''
    Класс для создания рассылки
    '''
    model = Mailing
    form_class = MailingForm
    permission_required = 'mailings.add_mailing'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form) -> HttpResponse:
        if form.is_valid():
            self.object = form.save()
            self.object.status = MailingStatus.objects.get(name='создана')
            self.object.slug = slugify(f'{self.object.title}-{self.object.pk}')
            self.object.user = self.request.user
            self.object.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание рассылки'

        return context


class MailingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    Класс для редактирования рассылки
    '''
    model = Mailing
    form_class = MailingForm
    permission_required = 'mailings.change_mailing'
    success_url = reverse_lazy('mailings:mailing_list')

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        mailing = self.get_object()

        if not check_user(mailing.user, self.request.user) or not check_mailing_status(mailing, 'создана'):
            return redirect('mailings:mailing_list')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse:
        if form.is_valid():
            self.object = form.save()
            self.object.slug = slugify(f'{self.object.title}-{self.object.pk}')
            self.object.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование рассылки {self.object.title}'

        return context


class MailingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    '''
    Класс для удаления рассылки
    '''
    model = Mailing
    permission_required = 'mailings.delete_mailing'

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        mailing = self.get_object()
        group = self.request.user.groups.filter(name='manager')

        if not group:
            if not check_user(mailing.user, self.request.user) or check_mailing_status(mailing, 'запущена'):
                return redirect('mailings:mailing_list')
        elif self.get_object().status != get_status_object('создана'):
            return redirect('mailings:manager_mailing_list')

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        group = self.request.user.groups.filter(name='manager')

        if group:
            return reverse('mailings:manager_mailing_list')

        return reverse('mailings:mailing_list')

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление рассылки {self.object.title}'

        return context


class ChangeMailingStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    '''
    Класс для перевода рассылки к типу "завершена"
    '''
    permission_required = 'mailings.change_mailingstatus'

    def __get_mailing(self, slug) -> Mailing:
        mailing = get_object_or_404(Mailing, slug=slug)

        return mailing

    def get(self, request, slug) -> HttpResponse:
        mailing = self.__get_mailing(slug)
        group = self.request.user.groups.filter(name='manager')

        if not group:
            if not check_user(mailing.user, self.request.user) or not check_mailing_status(mailing, 'запущена'):
                return redirect('mailings:mailing_list')
        elif not check_mailing_status(mailing, 'запущена'):
            return redirect('mailings:manager_mailing_list')

        return render(
            request, 'mailings/mailing_status_change.html',
            {'object': mailing, 'title': 'Изменение статуса'}
        )

    def post(self, request, slug) -> HttpResponse:
        mailing = self.__get_mailing(slug)
        mailing.status = MailingStatus.objects.get(name='завершена')
        mailing.save()

        group = self.request.user.groups.filter(name='manager')

        if group:
            return redirect('mailings:manager_mailing_list')

        return redirect('mailings:mailing_list')


class ClientListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    Класс для отображения всех клиентов
    '''
    model = Client
    permission_required = 'mailings.view_client'

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        queryset = super().get_queryset(*args, **kwargs)
        user = self.request.user
        queryset = queryset.filter(user=user)

        return queryset

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Клиенты'

        return context


class ClientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    '''
    Класс для отображения одного клиента
    '''
    model = Client
    permission_required = 'mailings.view_client'

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        if not check_user(self.get_object().user, self.request.user):
            return redirect('mailings:client_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.fullname

        return context


class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    '''
    Класс для создания клиента
    '''
    model = Client
    form_class = ClientForm
    permission_required = 'mailings.add_client'
    success_url = reverse_lazy('mailings:client_list')

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user, 'email': None})

        return kwargs

    def form_valid(self, form) -> HttpResponse:
        if form.is_valid():
            self.object = form.save()
            self.object.user = self.request.user
            self.object.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание клиента'

        return context


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    '''
    Класс для обновления клиента
    '''
    model = Client
    form_class = ClientForm
    permission_required = 'mailings.change_client'
    success_url = reverse_lazy('mailings:client_list')

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        if not check_user(self.get_object().user, self.request.user):
            return redirect('mailings:client_list')

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user, 'email': self.object.email})

        return kwargs

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование клиента {self.object.fullname}'

        return context


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    '''
    Класс для удаления клиента
    '''
    model = Client
    permission_required = 'mailings.delete_client'
    success_url = reverse_lazy('mailings:client_list')

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        if not check_user(self.get_object().user, self.request.user):
            return redirect('mailings:client_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление клиента {self.object.fullname}'

        return context


class MailingLogsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    Класс для просмотра всех логов рассылок
    '''
    model = MailingLogs
    permission_required = 'mailings.view_mailinglogs'
    template_name = 'mailings/mailing_logs_list.html'

    def get_queryset(self, *args, **kwargs) -> MailingLogs:
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(mailing__user=self.request.user).order_by('-attempt_datetime')

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Логи рассылок'

        return context


class ManagerMailingListView(MailingListView):
    '''
    Класс для отображения страницы всех активных рассылок для менеджера
    '''
    template_name = 'mailings/manager_mailing_list.html'
    permission_required = 'mailings.view_mailing'

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        queryset = Mailing.objects.filter(
            Q(status=get_status_object('запущена')) |
            Q(status=get_status_object('создана'))
        )

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Активные рассылки'

        return context

    def test_func(self) -> bool:
        return self.request.user.is_staff
