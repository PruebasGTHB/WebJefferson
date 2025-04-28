from django.db import models

# Create your models here.


class ConsumoEnergiaElectrica(models.Model):
    medidor = models.CharField(max_length=10)
    año = models.IntegerField(default=2025)
    mes = models.IntegerField()
    energia_total_kwh = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        db_table = 'consumo_energia_electrica'  # ✅ Aquí apuntas a tu tabla existente
        managed = False  # ✅ Esto es lo que faltaba poner



class ConsumoEnergiaTermica(models.Model):
    medidor = models.CharField(max_length=10)
    año = models.IntegerField(default=2025)
    mes = models.IntegerField()
    consumo_total_glp_kw = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        db_table = 'consumo_energia_termica_tabla'
        managed = False  # ✅ también aquí



class MedidorPosicion(models.Model):
    MEDIDOR_TIPO_CHOICES = [
        ('M', 'Medido'),
        ('C', 'Calculado'),
    ]

    CATEGORIA_CHOICES = [
        ('medidor', 'Medidor'),
        ('titulo', 'Título'),
    ]

    SECCION_CHOICES = [
    ('Vista General Planta', 'Vista General Planta'),
    ('Empalme 1 Planta Harina', 'Empalme 1 Planta Harina'),
    ('Empalme 2 Planta Congelado', 'Empalme 2 Planta Congelado'),
    ('Empalme 3 Pontón Tor', 'Empalme 3 Pontón Tor'),
    ('General Flota', 'General Flota'),
    ('Sala de Calderas', 'Sala de Calderas'),
    ('Planta Harina', 'Planta Harina'),
    ('Planta Congelado', 'Planta Congelado'),
    ('Flota', 'Flota'),
    ('Planta Harina/Congelados', 'Planta Harina/Congelados'),
]

    medidor_id = models.CharField(max_length=50)
    x = models.FloatField(default=4575.3279)
    y = models.FloatField(default=1941.9883)

    seccion = models.CharField(
        max_length=100,
        choices=SECCION_CHOICES,
        default='Vista General Planta',
    )

    tipo = models.CharField(
        max_length=1,
        choices=MEDIDOR_TIPO_CHOICES,
        default='M'
    )

    categoria_visual = models.CharField(
        max_length=50,
        choices=CATEGORIA_CHOICES,
        default='medidor',
        blank=True,
    )

    titulo = models.CharField(max_length=100, blank=True)
    grafana_url = models.URLField(blank=True, null=True)
    editable = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medidor_id} @ ({self.x}, {self.y})"

    class Meta:
        db_table = 'core_medidorposicion'
        constraints = [
            models.UniqueConstraint(
                fields=['medidor_id', 'seccion'], name='unique_medidor_por_seccion')
        ]


class ConexionMedidores(models.Model):
    SOCKET_OPTIONS = [
        ('top', 'Arriba'),
        ('bottom', 'Abajo'),
        ('left', 'Izquierda'),
        ('right', 'Derecha'),
    ]

    origen = models.ForeignKey(
        MedidorPosicion,
        on_delete=models.CASCADE,
        related_name='conexiones_salida',
        verbose_name="Medidor origen"
    )

    destino = models.ForeignKey(
        MedidorPosicion,
        on_delete=models.CASCADE,
        related_name='conexiones_entrada',
        verbose_name="Medidor destino"
    )

    start_socket = models.CharField(
        max_length=10,
        choices=SOCKET_OPTIONS,
        default='bottom',
        verbose_name="Socket origen",
        blank=True
    )

    end_socket = models.CharField(
        max_length=10,
        choices=SOCKET_OPTIONS,
        default='top',
        verbose_name="Socket destino",
        blank=True
    )

    descripcion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.origen.medidor_id} → {self.destino.medidor_id}"
