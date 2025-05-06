from django import forms
from .widgets import ColorTextWidget
from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import ConexionElemento, MedidorPosicion
from collections import defaultdict

#################################################################################################################################################################
#################################################################################################################################################################


class ConexionElementoSimplificadoForm(forms.ModelForm):

    SECCION_CHOICES = MedidorPosicion.SECCION_CHOICES

    seccion_ui = forms.ChoiceField(
        label='Sección',
        choices=SECCION_CHOICES,
        required=False
    )

    origen_ui = forms.ChoiceField(label='Origen')
    destino_ui = forms.ChoiceField(label='Destino')

    class Meta:
        model = ConexionElemento
        fields = ['seccion_ui', 'origen_ui', 'destino_ui',
                  'start_socket', 'end_socket', 'estilo_linea', 'descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        seccion_seleccionada = None

        if self.data.get('seccion_ui'):
            seccion_seleccionada = self.data.get('seccion_ui')
        elif self.initial.get('seccion_ui'):
            seccion_seleccionada = self.initial['seccion_ui']

        self.fields['origen_ui'].choices = self._build_grouped_choices(
            seccion_seleccionada)
        self.fields['destino_ui'].choices = self._build_grouped_choices(
            seccion_seleccionada)

    def _build_grouped_choices(self, seccion=None):
        grupos = defaultdict(list)

        queryset = MedidorPosicion.objects.all()
        if seccion:
            queryset = queryset.filter(seccion=seccion)

        for medidor in queryset.order_by('seccion', 'medidor_id'):
            grupo = medidor.seccion
            nombre = medidor.medidor_id or "(sin ID)"
            tipo = dict(MedidorPosicion.MEDIDOR_TIPO_CHOICES).get(
                medidor.tipo, 'Sin tipo')
            categoria = dict(MedidorPosicion.CATEGORIA_CHOICES).get(
                medidor.categoria_visual, 'Otro')
            etiqueta = f"[{categoria.capitalize()}] {nombre} ({tipo})"
            grupos[grupo].append((f"medidorposicion-{medidor.pk}", etiqueta))

        grupos_ordenados = []
        for seccion, elementos in sorted(grupos.items()):
            elementos.sort(key=lambda x: x[1])
            grupos_ordenados.append((seccion, elementos))

        return grupos_ordenados

    def save(self, commit=True):
        instance = super().save(commit=False)

        origen_tipo, origen_id = self.cleaned_data['origen_ui'].split('-')
        destino_tipo, destino_id = self.cleaned_data['destino_ui'].split('-')

        instance.origen_content_type = ContentType.objects.get(
            model=origen_tipo)
        instance.origen_object_id = origen_id
        instance.destino_content_type = ContentType.objects.get(
            model=destino_tipo)
        instance.destino_object_id = destino_id

        if commit:
            instance.save()
        return instance


#################################################################################################################################################################
#################################################################################################################################################################


class MedidorPosicionForm(forms.ModelForm):
    class Meta:
        model = MedidorPosicion
        fields = '__all__'
        widgets = {
            'fondo_personalizado': ColorTextWidget(),
            'color_titulo': ColorTextWidget(),
            'text_color': ColorTextWidget(),
            'background': ColorTextWidget(),
            'border_color': ColorTextWidget(),
        }

#################################################################################################################################################################
#################################################################################################################################################################


class DuplicarMedidoresForm(forms.Form):
    nueva_seccion = forms.ChoiceField(
        choices=MedidorPosicion.SECCION_CHOICES,
        label='Sección destino',
    )


#################################################################################################################################################################
#################################################################################################################################################################


class AjustarCoordenadasForm(forms.Form):
    delta_x = forms.CharField(label="Δ X")
    delta_y = forms.CharField(label="Δ Y")

    def clean_delta_x(self):
        valor = self.cleaned_data['delta_x'].replace(',', '.')
        return float(valor)

    def clean_delta_y(self):
        valor = self.cleaned_data['delta_y'].replace(',', '.')
        return float(valor)
