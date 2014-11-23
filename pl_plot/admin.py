from django.contrib import admin
from pl_plot.models import OverlayDefinition
from pl_plot.models import Overlay


class OverlayDefinitionAdmin(admin.ModelAdmin):
    readonly_fields = ('type', 'display_name_long', 'function_name')
    fields = ('is_base', 'display_name_short')

    list_display = ('display_name_long', 'function_name', 'type', 'is_base')
    list_per_page = 20


class OverlayAdmin(admin.ModelAdmin):
    pass

admin.site.register(Overlay, OverlayAdmin)
admin.site.register(OverlayDefinition, OverlayDefinitionAdmin)