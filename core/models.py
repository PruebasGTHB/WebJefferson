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
