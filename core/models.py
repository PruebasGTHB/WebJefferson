from django.db import models

# Create your models here.


class ConsumoEnergiaElectrica(models.Model):
    medidor = models.CharField(max_length=10)
    anio = models.IntegerField()
    mes = models.IntegerField()
    energia_total_kwh = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        db_table = 'consumo_energia_electrica'  # 🔄 Nombre real de la tabla


class ConsumoEnergiaTermica(models.Model):
    medidor = models.CharField(max_length=10)
    anio = models.IntegerField()
    mes = models.IntegerField()
    consumo_total_glp_kw = models.DecimalField(max_digits=10, decimal_places=1)

    class Meta:
        db_table = 'consumo_energia_termica_tabla'  # 🔄 Nombre real de la tabla


class MedidorPosicion(models.Model):
    medidor_id = models.CharField(max_length=50, unique=True)
    x = models.FloatField()
    y = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.medidor_id} @ ({self.x}, {self.y})"


class ConexionMedidores(models.Model):
    origen_id = models.CharField(max_length=50)
    destino_id = models.CharField(max_length=50)
    start_socket = models.CharField(max_length=20, default='bottom')
    end_socket = models.CharField(max_length=20, default='top')

    def __str__(self):
        return f"{self.origen_id} → {self.destino_id}"
