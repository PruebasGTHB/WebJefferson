from django.contrib import admin
from .models import MedidorPosicion, ConexionElemento, ConfiguracionInterfaz
from .forms import MedidorPosicionForm, ConexionElementoSimplificadoForm

##########################################################################################################################################################################################################################
##########################################################################################################################################################################################################################


class MedidorPosicionAdmin(admin.ModelAdmin):
    form = MedidorPosicionForm

    list_display = (
        'medidor_id', 'seccion', 'tipo', 'categoria_visual',
        'titulo', 'x', 'y', 'editable', 'updated_at'
    )
    list_filter = ('seccion', 'tipo', 'categoria_visual', 'editable')
    search_fields = ('medidor_id', 'titulo', 'seccion')
    ordering = ('seccion', 'medidor_id')
    readonly_fields = ('updated_at',)
    actions = ['activar_edicion', 'desactivar_edicion']

    fieldsets = (
        ('🧾 Datos Básicos', {
            'fields': ('medidor_id', 'seccion', 'categoria_visual')
        }),
        ('📐 Posición en Canvas', {
            'fields': ('x', 'y')
        }),
        ('⚙️ Configuración de Medidor', {
            'fields': ('titulo', 'tipo', 'tipo_descripcion', 'grafana_url'),
            'classes': ('collapse',)
        }),
        ('🎨 Configuración de Título', {
            'fields': (
                'seccion_destino', 'fondo_personalizado', 'color_titulo',
                'tamano_titulo', 'fuente_titulo', 'bold_titulo',
                'alineacion_vertical',
            ),
            'classes': ('collapse',)
        }),
        ('🔌 Configuración de Solo Energía', {
            'fields': (
                'tipo_icono_estado', 'mostrar_icono_estado'
            ),
            'classes': ('collapse',)
        }),
        ('🧱 Configuración de Texto', {
            'fields': (
                'width', 'height', 'background', 'border_color', 'border_width',
                'border_radius', 'border_style', 'animate_class', 'text_content',
                'text_color', 'font_size', 'text_align', 'text_vertical_align',
                'font_weight', 'font_style', 'text_decoration',
            ),
            'classes': ('collapse',)
        }),
        ('🔧 Configuración Especial', {
            'fields': ('editable',)
        }),
        ('⏱️ Tiempos', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )

    @admin.action(description="✅ Activar edición en los seleccionados")
    def activar_edicion(self, request, queryset):
        queryset.update(editable=True)

    @admin.action(description="🚫 Desactivar edición en los seleccionados")
    def desactivar_edicion(self, request, queryset):
        queryset.update(editable=False)

    class Media:
        # Si en el futuro necesitas JS personalizado, lo puedes dejar aquí
        js = ('admin/admin_medidor_condiciones.js',)


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


##########################################################################################################################################################################################################################
##########################################################################################################################################################################################################################


class ConfiguracionInterfazAdmin(admin.ModelAdmin):
    list_display = ['mostrar_cuadricula']


##########################################################################################################################################################################################################################
##########################################################################################################################################################################################################################


admin.site.register(ConfiguracionInterfaz, ConfiguracionInterfazAdmin)
admin.site.register(MedidorPosicion, MedidorPosicionAdmin)
admin.site.register(ConexionElemento, ConexionElementoAdmin)
