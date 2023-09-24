import datetime

from django.db.models import Q

from mailings.models import (
    Mailing, MailingStatus, MailingLogs, MailingRegularity, Client
)
from mailings.services import send_email


def cron_send_email() -> None:
    '''
    Функция отправляет e-mail рассылку всем клиентам пользователя в указанную
    дату с определенной часттой - раз в день, раз в неделю, раз в месяц
    или единоразово. При единоразовой отправке, статус рассылки меняется
    на "завершена". При первой отправке рассылки с указаной частотой,
    рассылка переходит на статус "запущена". После каждой рассылки с
    указанной частотой, дата следующей отправки увеличивается на указанный
    срок (день, 7 дней, 30 дней). После каждой рассылки её логи сохраняются
    и помещаются в базу данных.
    '''
    now = datetime.datetime.now()
    mailings = Mailing.objects.filter(
        Q(status=MailingStatus.objects.get(name='создана')) |
        Q(status=MailingStatus.objects.get(name='запущена'))
    )

    # перебор всех рассылок со статусом "создана" или "запущена"
    for mailing in mailings:
        try:
            # отправка e-mail рассылки, если настоящее время больше установленного для отправки
            if mailing.sending_time.timestamp() < now.timestamp():
                clients_email_list = [str(client.email) for client in Client.objects.filter(user=mailing.user)]
                send_email(mailing.title, mailing.body, clients_email_list)
                MailingLogs.objects.create(mailing=mailing)

                # изменение статуса рассылки на "запущена", если у нее имеется частота отправки
                if mailing.regularity:
                    mailing.status = MailingStatus.objects.get(name='запущена')
                    mailing.save()
                    # увелечение даты следующей отправки
                    if mailing.regularity == MailingRegularity.objects.get(name='раз в день'):
                        mailing.sending_time += datetime.timedelta(days=1)
                    elif mailing.regularity == MailingRegularity.objects.get(name='раз в неделю'):
                        mailing.sending_time += datetime.timedelta(days=7)
                    else:
                        mailing.sending_time += datetime.timedelta(days=30)
                else:
                    mailing.status = MailingStatus.objects.get(name='завершена')

                mailing.save()
        except Exception as e:
            MailingLogs.objects.create(mailing=mailing, status=False, server_response=f'{e}')
