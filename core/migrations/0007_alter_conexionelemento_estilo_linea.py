# Generated by Django 5.1.6 on 2025-05-06 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_medidorposicion_categoria_visual_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conexionelemento',
            name='estilo_linea',
            field=models.CharField(blank=True, choices=[('cyan-grid', 'Cian Grid'), ('red-straight', 'Rojo Recto'), ('green-fluid', 'Verde Fluido'), ('orange-arc', 'Naranja Arco'), ('blue-magnet', 'Azul Magneto'), ('purple-curve', 'Púrpura Curva'), ('gray-straight', 'Gris Recto'), ('pink-line', 'Rosado Lineal'), ('lime-grid', 'Lima Grid'), ('amber-path', 'Ámbar Camino'), ('ani-grey-grid', '🌀 Gris Animado Grid'), ('ani-orange-arc', '🌀 Naranja Animado Arco'), ('ani-blue-fluid', '🌀 Azul Animado Fluido'), ('ani-red-straight', '🌀 Rojo Animado Recto'), ('ani-teal-magnet', '🌀 Teal Magneto'), ('ani-indigo-dash', '🌀 Índigo Dash'), ('ani-yellow-blink', '🌀 Amarillo Blink'), ('ani-cyan-fade', '🌀 Cian Fade'), ('ani-green-pulse', '🌀 Verde Pulso'), ('ani-violet-spark', '🌀 Violeta Spark'), ('ani-brown-glow', '🌀 Marrón Glow'), ('ani-charcoal-arc', '🌀 Carbón Arco'), ('ani-maroon-fluid', '🌀 Marrón Fluido'), ('ani-beige-magnet', '🌀 Beige Magnet'), ('ani-navy-curve', '🌀 Azul Marino Curva')], default='ani-pink-grid', max_length=30, verbose_name='Estilo visual'),
        ),
    ]
