# Generated by Django 5.1.6 on 2025-05-05 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_medidorposicion_border_radius_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medidorposicion',
            name='font_weight',
            field=models.CharField(blank=True, choices=[('normal', 'Normal'), ('bold', 'Negrita')], default='bold', max_length=20, null=True),
        ),
    ]
