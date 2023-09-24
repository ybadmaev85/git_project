from django.contrib import admin

from mailings.models import (
    Client, MailingRegularity, MailingStatus, Mailing, MailingLogs
)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'fullname',)
    search_fields = ('email',)
    ordering = ('pk',)


@admin.register(MailingRegularity)
class MailingRegularityAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name',)
    ordering = ('pk',)


@admin.register(MailingStatus)
class MailingStatusAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name',)
    ordering = ('pk',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('title', 'sending_time', 'regularity', 'status',)
    list_filter = ('status',)
    search_fields = ('title', 'body',)
    ordering = ('-sending_time',)


@admin.register(MailingLogs)
class MailingLogsAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'attempt_datetime', 'status',)
    list_filter = ('status',)
    ordering = ('-attempt_datetime',)
