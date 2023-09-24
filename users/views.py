import string
import random

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, TemplateView, ListView, DetailView

from mailings.models import Mailing
from mailings.services import send_email, get_status_object

from typing import Any

from users.forms import RegisterForm, ResetPasswordForm
from users.models import User


class UserRegisterView(UserPassesTestMixin, CreateView):
    '''
    Класс для регистрации пользователей
    '''
    model = User
    template_name = 'users/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form) -> HttpResponse:
        if form.is_valid():
            self.object = form.save()
            self.object.is_active = False
            self.object.save()

            # генерация токена и uid зарегестрированого пользователя для его дальнейшей активации
            token = default_token_generator.make_token(self.object)
            uid = urlsafe_base64_encode(force_bytes(self.object.id))
            active_url = reverse_lazy('users:email_confirm', kwargs={'uidb64': uid, 'token': token})

            # отправка e-mail сообщения с ссылкой на активацию пользователя
            send_email(
                'Подтверждение e-mail адреса!',
                f'Чтобы подтвердить Ваш e-mail адрес, перейдите по ссылке: http://127.0.0.1:8000{active_url}',
                [self.object.email]
            )

            return redirect('users:email_sent_confirm')

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Регистрация'

        return context_data

    def test_func(self):
        return self.request.user.is_anonymous


class UserConfirmEmailView(UserPassesTestMixin, View):
    '''
    Класс для подтверждения e-mail адреса
    '''

    def get(self, request, uidb64, token) -> HttpResponse:
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except:
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            group = Group.objects.get(name='service_users')
            user.groups.add(group)
            user.is_active = True
            user.save()

            return redirect('users:email_confirmed')
        else:
            return redirect('users:email_fail_confirm')

    def test_func(self):
        return self.request.user.is_anonymous


class UserSentConfirmEmail(UserPassesTestMixin, TemplateView):
    '''
    Класс для отображения шаблона с успешной отправкой письма
    '''
    template_name = 'users/email_sent_confirm.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Письмо отправлено'

        return context_data

    def test_func(self):
        return self.request.user.is_anonymous


class UserConfirmedEmail(UserPassesTestMixin, TemplateView):
    '''
    Класс для отображения шаблона о подтверждении e-mail адреса
    '''
    template_name = 'users/email_confirmed.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'E-mail подтвержден'

        return context_data

    def test_func(self):
        return self.request.user.is_anonymous


class UserFailConfirmEmail(UserPassesTestMixin, TemplateView):
    '''
    Класс для отображения шаблона об ошибке при подверждение e-mail адреса
    '''
    template_name = 'users/email_fail_confirm.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Ошибка подтверждения'

        return context_data

    def test_func(self):
        return self.request.user.is_anonymous


class UserLoginView(UserPassesTestMixin, LoginView):
    '''
    Класс для авторизации пользователей
    '''
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Авторизация'

        return context_data

    def test_func(self):
        return self.request.user.is_anonymous


class UserPasswordResetView(UserPassesTestMixin, View):
    '''
    Класс для сброса пароля пользователя сервиса
    '''

    def get(self, request) -> HttpResponse:
        form = ResetPasswordForm

        return render(request, 'users/password_reset_form.html', {'form': form, 'title': 'Сброс пароля'})

    def post(self, request) -> HttpResponse:
        form = ResetPasswordForm(request.POST)

        if form.is_valid():
            user = User.objects.get(email=request.POST.get('email'))
            symbols = string.ascii_letters + string.digits
            password = ''.join(str(random.choice(symbols)) for _ in range(10))
            user.set_password(password)
            user.save()

            send_email(
                'Ваш новый пароль!',
                f'Ваш пароль для входа в систему: {password}',
                [user.email]
            )

            return redirect('users:password_sent_email')

        return render(request, 'users/password_reset_form.html', {'form': form, 'title': 'Сброс пароля'})

    def test_func(self):
        return self.request.user.is_anonymous


class UserSentPassword(UserPassesTestMixin, TemplateView):
    '''
    Класс для отображения шаблона об успешной отправки нового пароля
    '''
    template_name = 'users/password_sent_email.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'Новый пароль отправлен'

        return context_data

    def test_func(self):
        return self.request.user.is_anonymous


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, ListView):
    '''
    Класс для просмотра всех пользователей сервиса
    '''
    model = User
    permission_required = 'users.view_user'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Пользователи'

        return context

    def test_func(self) -> bool:
        return self.request.user.is_staff


class UserDetailView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, DetailView):
    '''
    Класс для просмотра одного пользователя сервиса
    '''
    model = User
    permission_required = 'users.view_user'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.object

        context['title'] = f'{self.object.email}'
        context['total_mailings'] = len(Mailing.objects.filter(user=user))
        context['created_mailings'] = len(Mailing.objects.filter(user=user, status=get_status_object('создана')))
        context['running_mailings'] = len(Mailing.objects.filter(user=user, status=get_status_object('запущена')))
        context['user'] = self.request.user

        return context

    def test_func(self) -> bool:
        return self.request.user.is_staff


class UserChangeActive(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, View):
    '''
    Класс для изменения поля is_active у пользователя сервиса
    '''
    permission_required = 'users.change_user'

    def __get_user(self, pk) -> User:
        user = get_object_or_404(User, pk=pk)

        return user

    def get(self, request, pk) -> HttpResponse:
        user = self.__get_user(pk)

        if user.is_active:
            title = 'Блокировка пользователя'
        else:
            title = 'Разблокировка пользователя'

        return render(request, 'users/user_change_active.html', {'object': user, 'title': title})

    def post(self, request, pk) -> HttpResponse:
        user = self.__get_user(pk)

        if user.is_active:
            user.is_active = False
            for mailing in user.mailing_set.all():
                mailing.status = get_status_object('завершена')
                mailing.save()
        else:
            user.is_active = True

        user.save()

        return redirect('users:user_list')

    def test_func(self) -> bool:
        return self.request.user.is_staff
