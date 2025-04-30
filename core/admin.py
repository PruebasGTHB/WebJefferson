from django.contrib import admin
from .models import MedidorPosicion, ConexionElemento, BloqueVisual, ConfiguracionInterfaz
from .forms import BloqueVisualForm, ConexionElementoSimplificadoForm

##########################################################################################################################################################################################################################
##########################################################################################################################################################################################################################


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

##########################################################################################################################################################################################################################
##########################################################################################################################################################################################################################


class ConexionElementoAdmin(admin.ModelAdmin):
    form = ConexionElementoSimplificadoForm

    list_display = (
        'mostrar_origen',
        'mostrar_destino',
        'start_socket',
        'end_socket',
        'estilo_linea',  # ✅ Añadido para mostrar el estilo en la tabla
    )

    def mostrar_origen(self, obj):
        return str(obj.origen)

    def mostrar_destino(self, obj):
        return str(obj.destino)


##########################################################################################################################################################################################################################
##########################################################################################################################################################################################################################


class BloqueVisualAdmin(admin.ModelAdmin):
    form = BloqueVisualForm

    list_display = ('div_id', 'seccion', 'x', 'y', 'width', 'height',
                    'background', 'border_color', 'text_content', 'editable', 'updated_at')
    list_filter = ('seccion', 'editable')
    search_fields = ('div_id', 'seccion', 'background',
                     'border_color', 'text_content')
    ordering = ('seccion', 'div_id')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Identificación y Ubicación', {
            'fields': ('div_id', 'seccion', 'x', 'y')
        }),
        ('Estilos del Div', {
            'fields': ('width', 'height', 'background', 'border_color', 'border_width', 'border_radius', 'border_style', 'animate_class')
        }),
        ('Texto dentro del Div', {
            'fields': ('text_content', 'text_color', 'font_size', 'text_align', 'text_vertical_align', 'font_weight', 'font_style', 'text_decoration')
        }),
        ('Configuración', {
            'fields': ('editable',),
        }),
        ('Tiempos', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )

##########################################################################################################################################################################################################################
##########################################################################################################################################################################################################################


class ConfiguracionInterfazAdmin(admin.ModelAdmin):
    list_display = ['mostrar_cuadricula']


##########################################################################################################################################################################################################################
##########################################################################################################################################################################################################################


admin.site.register(BloqueVisual, BloqueVisualAdmin)
admin.site.register(ConfiguracionInterfaz, ConfiguracionInterfazAdmin)
admin.site.register(MedidorPosicion, MedidorPosicionAdmin)
admin.site.register(ConexionElemento, ConexionElementoAdmin)
