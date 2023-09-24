from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class RegisterForm(UserCreationForm):
    '''
    Форма регистрации пользователей сервиса
    '''

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2',)


class ResetPasswordForm(forms.Form):
    '''
    Форма сброса пароля
    '''
    email = forms.EmailField(max_length=254, label='e-mail')

    def clean_email(self) -> str:
        cleaned_data = self.cleaned_data['email']
        try:
            user = User.objects.get(email=cleaned_data)
            if not user.is_active:
                raise forms.ValidationError('Пользователь с такими данными не существует или не подтвержден!')
        except User.DoesNotExist:
            raise forms.ValidationError('Пользователь с такими данными не существует или не подтвержден!')

        return cleaned_data
