from django.contrib import admin
from pl_download.models import DataFile


class DownloadAdmin(admin.ModelAdmin):

    # Decides which fields to show when changing data file
    readonly_fields = ('type', 'download_datetime', 'generated_datetime', 'model_date', 'file')

    # Decides what to display in listing of files in database
    list_display = ('file', 'model_date', 'generated_datetime')
    list_per_page = 100

    actions_on_top = True


admin.site.register(DataFile, DownloadAdmin)