from django.contrib import admin
from .models import MedidorPosicion, ConexionMedidores


class MedidorPosicionAdmin(admin.ModelAdmin):
    list_display = ('medidor_id', 'seccion', 'tipo',
                    'categoria_visual', 'titulo', 'x', 'y', 'editable', 'updated_at')
    list_filter = ('seccion', 'tipo', 'categoria_visual', 'editable')
    search_fields = ('medidor_id', 'titulo', 'seccion')
    ordering = ('seccion', 'medidor_id')
    readonly_fields = ('updated_at',)
    actions = ['activar_edicion', 'desactivar_edicion']

    fieldsets = (
        ('Identificación', {
            'fields': ('medidor_id', 'seccion', 'tipo', 'categoria_visual', 'titulo')
        }),
        ('Posición en Canvas', {
            'fields': ('x', 'y')
        }),
        ('Visualización de Datos', {
            'fields': ('grafana_url',)  # ✅ Solo grafana_url
        }),
        ('Configuración Especial', {
            'fields': ('editable',),
        }),
        ('Tiempos', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.action(description="✅ Activar edición en los seleccionados")
    def activar_edicion(self, request, queryset):
        queryset.update(editable=True)

    @admin.action(description="🚫 Desactivar edición en los seleccionados")
    def desactivar_edicion(self, request, queryset):
        queryset.update(editable=False)



class ConexionMedidoresAdmin(admin.ModelAdmin):
    list_display = ('origen', 'destino', 'start_socket', 'end_socket')
    list_filter = ('start_socket', 'end_socket')
    search_fields = (
        'origen__medidor_id',
        'origen__titulo',
        'destino__medidor_id',
        'destino__titulo',
    )
    autocomplete_fields = ['origen', 'destino']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['start_socket'].required = False
        form.base_fields['end_socket'].required = False
        return form


admin.site.register(MedidorPosicion, MedidorPosicionAdmin)
admin.site.register(ConexionMedidores, ConexionMedidoresAdmin)
