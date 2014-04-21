from django.contrib import admin
from pl_download.models import DataFile


class AuthorAdmin(admin.ModelAdmin):
    fields = ('type', 'download_date', 'generated_date', 'model_date', 'file')
admin.site.register(DataFile, AuthorAdmin)
