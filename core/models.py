from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

# Create your models here.


####################################################################################################################################################################
####################################################################################################################################################################


####################################################################################################################################################################
####################################################################################################################################################################


class ConsumoEnergiaElectrica(models.Model):
    medidor = models.CharField(max_length=10)
    año = models.IntegerField(default=2025)
    mes = models.IntegerField()
    energia_total_kwh = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        db_table = 'energia_electrica'
        managed = False


####################################################################################################################################################################


class ConsumoEnergiaTermica(models.Model):
    medidor = models.CharField(max_length=10)
    año = models.IntegerField(default=2025)
    mes = models.IntegerField()
    consumo_total_glp_kw = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        db_table = 'potencia_activa'
        managed = False


####################################################################################################################################################################
####################################################################################################################################################################


class MedidorPosicion(models.Model):
    MEDIDOR_TIPO_CHOICES = [
        ('M', 'Medido'),
        ('C', 'Calculado'),
        ('', 'Sin tipo'),
    ]

    CATEGORIA_CHOICES = [
        ('medidor', 'Medidor'),
        ('titulo', 'Título'),
        ('energia_sola', 'Solo Energía'),
        ('texto', 'Texto'),
        ('contenedor', 'Contenedor'),
        ('contenedor-10', 'Contenedor-10'),
        ('contenedor-100', 'Contenedor-100'),
        ('medidorglp', 'Medidor GLP'),
        ('medidordiesel', 'Medidor Diésel'),
        ('medidorvapor', 'Medidor de Vapor'),
        ('medidorflujometro', 'Medidor de Flujometro'),

    ]
    mostrar_icono_estado = models.BooleanField(default=False)
    # En caso quieras permitir variantes futuras
    tipo_icono_estado = models.CharField(
        max_length=50, blank=True, default='check')

    SECCION_CHOICES = [
        ('Vista General Planta', 'Vista General Planta'),
        ('Empalme 1 Planta Harina', 'Empalme 1 Planta Harina'),
        ('Empalme 2 Planta Congelado', 'Empalme 2 Planta Congelado'),
        ('Empalme 3 Pontón Tor', 'Empalme 3 Pontón Tor'),
        ('General', 'General'),
        ('Sala de Calderas', 'Sala de Calderas'),
        ('Planta Harina', 'Planta Harina'),
        ('Planta Congelado', 'Planta Congelado'),
        ('Flota', 'Flota'),
        ('Planta Harina/Congelados', 'Planta Harina/Congelados'),
    ]

    # Campos de personalización visual para títulos
    fondo_personalizado = models.CharField(
        max_length=50, blank=True, null=True, help_text="Ej: 'transparent', '#0044cc', 'rgba(0,0,0,0.5)'")
    color_titulo = models.CharField(
        max_length=50, blank=True, null=True, help_text="Ej: 'white', '#FFDD00'")
    tamano_titulo = models.CharField(
        max_length=10, blank=True, null=True, help_text="Ej: '16px'")
    fuente_titulo = models.CharField(
        max_length=100, blank=True, null=True, help_text="Ej: 'Arial', 'Verdana'")
    bold_titulo = models.BooleanField(default=False)
    alineacion_vertical = models.CharField(max_length=10, choices=[(
        'top', 'Arriba'), ('center', 'Centro'), ('bottom', 'Abajo')], default='center')

    medidor_id = models.CharField(max_length=50, blank=True, null=True)
    x = models.FloatField(default=13800.0000)
    y = models.FloatField(default=5531.0000)

    seccion = models.CharField(
        max_length=100,
        choices=SECCION_CHOICES,
        default='Planta Harina',
    )

    tipo = models.CharField(
        max_length=1,
        choices=MEDIDOR_TIPO_CHOICES,
        default='M',
        blank=True  # ✅ permite guardar vacío
    )

    tipo_descripcion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Texto que aparece al pasar el mouse sobre el tipo (M o C)"
    )

    categoria_visual = models.CharField(
        max_length=50,
        choices=CATEGORIA_CHOICES,
        default='texto',
        blank=True,
    )

    titulo = models.CharField(max_length=100, blank=True)
    grafana_url = models.URLField(blank=True, null=True)

    seccion_destino = models.CharField(
        max_length=100,
        choices=SECCION_CHOICES,
        blank=True,
        null=True,
    )
    # Estilos generales para bloques
    width = models.CharField(max_length=10, blank=True,
                             null=True, default='10px')
    height = models.CharField(
        max_length=10, blank=True, null=True, default='10px')
    background = models.CharField(
        max_length=50, blank=True, null=True, default='white')
    border_color = models.CharField(max_length=50, blank=True, null=True)
    border_width = models.CharField(
        max_length=10, blank=True, null=True, default='1px')
    border_radius = models.CharField(
        max_length=10, blank=True, null=True, default='5px')
    border_style = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('solid', 'Sólido'),
            ('dashed', 'Guiones'),
            ('dotted', 'Punteado'),
            ('double', 'Doble'),
            ('groove', 'Surco'),
        ],
        default='solid'
    )
    animate_class = models.CharField(max_length=100, blank=True, null=True)

    # Texto interno
    text_content = models.TextField(blank=True, null=True)
    z_index = models.IntegerField(
        blank=True,
        null=True,
        help_text="Valor de z-index para controlar la superposición. Ej: 10, 100, etc."
    )

    # Estilo de texto
    text_color = models.CharField(
        max_length=20, blank=True, null=True, default='#000000')
    font_size = models.CharField(
        max_length=10, blank=True, null=True, default='16px')
    text_align = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[('left', 'Izquierda'), ('center',
                                         'Centro'), ('right', 'Derecha')],
        default='center'
    )
    text_vertical_align = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[('start', 'Arriba'), ('center', 'Centro'), ('end', 'Abajo')],
        default='start'
    )
    font_weight = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[('normal', 'Normal'), ('bold', 'Negrita')],
        default='bold'
    )
    font_style = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[('normal', 'Normal'), ('italic', 'Cursiva')],
        default='normal'
    )
    text_decoration = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[('none', 'Ninguno'), ('underline', 'Subrayado')],
        default='none'
    )
    # Agregar al modelo MedidorPosicion
    energia_total_kwh = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, help_text="Valor fijo si no se consulta por API")
    potencia_total_kw = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, help_text="Valor fijo si no se consulta por API")
    kg_totalizador = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, help_text="Valor fijo si no se consulta por API")

    editable = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medidor_id or '(Sin ID)'} @ {self.seccion} ({self.x:.2f}, {self.y:.2f})"

    class Meta:
        db_table = 'core_medidorposicion'
        constraints = [
            models.UniqueConstraint(
                fields=['medidor_id', 'seccion'], name='unique_medidor_por_seccion')
        ]

####################################################################################################################################################################
####################################################################################################################################################################


class ConexionElemento(models.Model):

    SOCKET_OPTIONS = [
        ('top', 'Arriba'),
        ('bottom', 'Abajo'),
        ('left', 'Izquierda'),
        ('right', 'Derecha'),
    ]

    # Origen genérico
    origen_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='origen_tipo')
    origen_object_id = models.CharField(max_length=100)
    origen = GenericForeignKey('origen_content_type', 'origen_object_id')

    # Destino genérico
    destino_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='destino_tipo')
    destino_object_id = models.CharField(max_length=100)
    destino = GenericForeignKey('destino_content_type', 'destino_object_id')

    start_socket = models.CharField(
        max_length=10,
        choices=SOCKET_OPTIONS,
        default='right',
        blank=True
    )

    end_socket = models.CharField(
        max_length=10,
        choices=SOCKET_OPTIONS,
        default='left',
        blank=True
    )

    ESTILO_LINEA_CHOICES = [
        ('azul-solido', 'Azul-solido'),
        ('yellow-straight', 'Amarillo Solido'),
        ('green-fluid', 'Verde Fluido'),
        ('orange-arc', 'Naranja Arco'),
        ('blue-magnet', 'Azul Magneto'),
        ('purple-curve', 'Púrpura Curva'),
        ('gray-straight', 'Gris Recto'),
        ('pink-line', 'Rosado Lineal'),
        ('lime-grid', 'Lima Grid'),
        ('amber-path', 'Ámbar Camino'),

        # Animadas
        ('ani-pink-grid', '🌀 Gris Animado Grid'),
        ('ani-orange-arc', '🌀 Naranja Animado Grid'),
        ('ani-blue-fluid', '🌀 Azul Animado Grid'),
        ('ani-red-straight', '🌀 Rojo Animado Grid'),
        ('ani-green-magnet', '🌀 Verde Animado Grid'),
        ('ani-yellow-dash', '🌀 Amarillo Animado Grid'),
        ('ani-yellow-blink', '🌀 Amarillo Blink'),
        ('ani-cyan-fade', '🌀 Cian Fade'),
        ('ani-green-pulse', '🌀 Verde Pulso'),
        ('ani-violet-spark', '🌀 Violeta Spark'),
        ('ani-brown-glow', '🌀 Marrón Glow'),
        ('ani-charcoal-arc', '🌀 Carbón Arco'),
        ('ani-maroon-fluid', '🌀 Marrón Fluido'),
        ('ani-beige-magnet', '🌀 Beige Magnet'),
        ('ani-navy-curve', '🌀 Azul Marino Curva'),
    ]

    estilo_linea = models.CharField(
        max_length=30,
        choices=ESTILO_LINEA_CHOICES,
        default='ani-orange-arc',
        blank=True,
        verbose_name="Estilo visual"
    )

    descripcion = models.CharField(max_length=200, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.origen} → {self.destino}"


####################################################################################################################################################################
####################################################################################################################################################################


class ConfiguracionInterfaz(models.Model):
    mostrar_cuadricula = models.BooleanField(default=False)

    def __str__(self):
        return "Configuración de la Interfaz"


####################################################################################################################################################################
####################################################################################################################################################################
