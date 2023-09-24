from django.contrib.auth.views import LogoutView
from django.urls import path
from django.views.decorators.cache import cache_page

from users.apps import UsersConfig
from users.views import (
    UserRegisterView, UserLoginView, UserSentConfirmEmail, UserConfirmEmailView,
    UserConfirmedEmail, UserFailConfirmEmail, UserPasswordResetView, UserSentPassword,
    UserListView, UserChangeActive, UserDetailView
)

app_name = UsersConfig.name

urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('sent_confirm_email/', cache_page(3600)(UserSentConfirmEmail.as_view()), name='email_sent_confirm'),
    path('confirm_email/<str:uidb64>/<str:token>/', UserConfirmEmailView.as_view(), name='email_confirm'),
    path('confirmed_email/', cache_page(3600)(UserConfirmedEmail.as_view()), name='email_confirmed'),
    path('fail_confirm_email/', cache_page(3600)(UserFailConfirmEmail.as_view()), name='email_fail_confirm'),
    path('password_reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password_sent_email/', cache_page(3600)(UserSentPassword.as_view()), name='password_sent_email'),
    path('change_active/<int:pk>/', UserChangeActive.as_view(), name='user_change_active'),
]