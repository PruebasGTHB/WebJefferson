from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

from .models import MedidorPosicion, ConexionElemento, ConfiguracionInterfaz
from .forms import (
    MedidorPosicionForm,
    ConexionElementoSimplificadoForm,
    DuplicarMedidoresForm,
    AjustarCoordenadasForm,
)


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

    actions = [
        'ajustar_coordenadas',
        'activar_edicion',
        'desactivar_edicion',
        'duplicar_medidores',
    ]

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
            'fields': ('tipo_icono_estado', 'mostrar_icono_estado'),
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('duplicar/', self.admin_site.admin_view(self.duplicar_medidores_view),
                 name='duplicar_medidores'),
            path('ajustar-coordenadas/', self.admin_site.admin_view(
                self.ajustar_coordenadas_view), name='ajustar_coordenadas'),
        ]
        return custom_urls + urls

    @admin.action(description="📍 Ajustar coordenadas de posición")
    def ajustar_coordenadas(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        if not selected:
            self.message_user(
                request, "⚠️ No se seleccionó ningún medidor.", level=messages.WARNING)
            return redirect('admin:core_medidorposicion_changelist')

        selected_params = '&'.join(f'_selected_action={pk}' for pk in selected)
        return HttpResponseRedirect(f"/admin/core/medidorposicion/ajustar-coordenadas/?{selected_params}")

    def ajustar_coordenadas_view(self, request):
        selected_ids = request.GET.getlist('_selected_action')
        medidores = MedidorPosicion.objects.filter(id__in=selected_ids)

        if request.method == 'POST':
            form = AjustarCoordenadasForm(request.POST)
            if form.is_valid():
                dx = form.cleaned_data['delta_x']
                dy = form.cleaned_data['delta_y']

                for m in medidores:
                    m.x += dx
                    m.y += dy
                    m.save()

                self.message_user(
                    request, f"✅ Coordenadas actualizadas en {len(medidores)} medidor(es).", level=messages.SUCCESS)
                return redirect('admin:core_medidorposicion_changelist')
        else:
            form = AjustarCoordenadasForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            medidores=medidores,
        )
        return render(request, 'core/ajustar_coordenadas_form/ajustar_coordenadas_form.html', context)

    @admin.action(description="✅ Activar edición en los seleccionados")
    def activar_edicion(self, request, queryset):
        queryset.update(editable=True)

    @admin.action(description="🚫 Desactivar edición en los seleccionados")
    def desactivar_edicion(self, request, queryset):
        queryset.update(editable=False)

    @admin.action(description="📄 Duplicar en otra sección")
    def duplicar_medidores(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        if not selected:
            self.message_user(
                request, "⚠️ No se seleccionó ningún medidor.", level=messages.WARNING)
            return redirect('admin:core_medidorposicion_changelist')

        selected_params = '&'.join(f'_selected_action={pk}' for pk in selected)
        return redirect(f"/admin/core/medidorposicion/duplicar/?{selected_params}")

    def duplicar_medidores_view(self, request):
        if request.method == 'POST':
            form = DuplicarMedidoresForm(request.POST)
            if form.is_valid():
                nueva_seccion = form.cleaned_data['nueva_seccion']
                selected_ids = request.POST.getlist('_selected_action')
                if not selected_ids:
                    self.message_user(
                        request, "⚠️ No se seleccionó ningún medidor.", level=messages.WARNING)
                    return redirect('admin:core_medidorposicion_changelist')

                medidores = MedidorPosicion.objects.filter(id__in=selected_ids)
                duplicados = 0

                for m in medidores:
                    m.pk = None
                    m.seccion = nueva_seccion
                    m.save()
                    duplicados += 1

                self.message_user(
                    request, f"✅ Se duplicaron {duplicados} medidor(es) en '{nueva_seccion}'.", level=messages.SUCCESS)
                return redirect('admin:core_medidorposicion_changelist')
        else:
            selected_ids = request.GET.getlist('_selected_action')
            medidores = MedidorPosicion.objects.filter(id__in=selected_ids)
            form = DuplicarMedidoresForm()

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            medidores=medidores,
        )
        return render(request, 'core/duplicar_medidores/duplicar_medidores_form.html', context)

    class Media:
        js = ('admin/admin_medidor_condiciones.js',)


admin.site.register(MedidorPosicion, MedidorPosicionAdmin)


class ConexionElementoAdmin(admin.ModelAdmin):
    form = ConexionElementoSimplificadoForm
    list_display = (
        'mostrar_origen',
        'mostrar_destino',
        'start_socket',
        'end_socket',
        'estilo_linea',
    )

    def mostrar_origen(self, obj):
        return str(obj.origen)

    def mostrar_destino(self, obj):
        return str(obj.destino)

    class Media:
        # 🔁 Esto permite la recarga automática al cambiar sección
        js = ('admin/conexion_filtro_seccion.js',)


class ConfiguracionInterfazAdmin(admin.ModelAdmin):
    list_display = ['mostrar_cuadricula']


admin.site.register(ConexionElemento, ConexionElementoAdmin)
admin.site.register(ConfiguracionInterfaz, ConfiguracionInterfazAdmin)
