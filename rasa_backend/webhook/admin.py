from django.contrib import admin

from webhook.models import Page


# Register your models here.
class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'href', 'title')


admin.site.register(Page, PageAdmin)
