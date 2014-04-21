from django.contrib import admin
from pl_plot.models import OverlayDefinition


class AuthorAdmin(admin.ModelAdmin):
    fields = ('type', 'display_name_long', 'display_name_short', 'function_name', 'is_base')
admin.site.register(OverlayDefinition, AuthorAdmin)
