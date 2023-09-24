from datetime import datetime

from django import forms

from mailings.models import Mailing, Client


class MailingForm(forms.ModelForm):
    '''
    Форма рассылки сервиса
    '''

    class Meta:
        model = Mailing
        fields = ('title', 'body', 'sending_time', 'regularity',)
        widgets = {'sending_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['sending_time'].help_text = 'Рассылка должна быть опубликована не ранее, ' \
                                                'чем через минуту от текущего времени.'

    def clean_sending_time(self) -> datetime:
        cleaned_data = self.cleaned_data['sending_time']

        if cleaned_data.timestamp() <= datetime.now().timestamp():
            raise forms.ValidationError('Рассылка должна иметь достоверное время')

        return cleaned_data


class ClientForm(forms.ModelForm):
    '''
    Форма клиента сервиса
    '''

    class Meta:
        model = Client
        fields = ('fullname', 'email', 'comment',)

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user')
        self.email = kwargs.pop('email')

        super().__init__(*args, **kwargs)

    def clean_email(self) -> str:
        cleaned_data = self.cleaned_data['email']

        if cleaned_data != self.email:
            is_existed = Client.objects.filter(email=cleaned_data, user=self.user).exists()

            if is_existed:
                raise forms.ValidationError('Пользователь с таким e-mail существует!')

        return cleaned_data
