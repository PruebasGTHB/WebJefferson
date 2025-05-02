from django import forms
from .widgets import ColorTextWidget
from django import forms
from django.contrib.contenttypes.models import ContentType
from .models import ConexionElemento, MedidorPosicion
from collections import defaultdict

#################################################################################################################################################################
#################################################################################################################################################################


class ConexionElementoSimplificadoForm(forms.ModelForm):
    origen_ui = forms.ChoiceField(label='Origen')
    destino_ui = forms.ChoiceField(label='Destino')

    class Meta:
        model = ConexionElemento
        fields = ['origen_ui', 'destino_ui', 'start_socket',
                  'end_socket', 'estilo_linea', 'descripcion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['origen_ui'].choices = self._build_grouped_choices()
        self.fields['destino_ui'].choices = self._build_grouped_choices()

        if self.instance.pk:
            origen_model = self.instance.origen_content_type.model
            destino_model = self.instance.destino_content_type.model
            self.fields['origen_ui'].initial = f"{origen_model}-{self.instance.origen_object_id}"
            self.fields['destino_ui'].initial = f"{destino_model}-{self.instance.destino_object_id}"

    def _build_grouped_choices(self):
        grupos = defaultdict(list)

        for medidor in MedidorPosicion.objects.all():
            display = f"[MEDIDOR] {medidor.medidor_id or '(sin ID)'}"
            grupos[medidor.seccion].append(
                (f"medidorposicion-{medidor.pk}", display))

        return [(seccion, opciones) for seccion, opciones in sorted(grupos.items())]

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
