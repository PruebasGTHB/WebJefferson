from django.db import connection
from django.http import JsonResponse
from datetime import datetime
from collections import defaultdict


from rest_framework.decorators import api_view


@api_view(['GET'])
def demanda_refrigeracion(request):
    fecha_inicio = request.GET.get('inicio', '2025-01-01')
    fecha_fin = request.GET.get('fin', '2025-02-27')

    compresores = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']
    tuneles = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10']

    def get_metric_data(tags, tabla, campo_valor):
        resultados = []
        for tag in tags:
            with connection.cursor() as cursor:
                cursor.execute(f'''
                    SELECT fecha, {campo_valor}
                    FROM {tabla}
                    WHERE tag = %s
                    AND fecha BETWEEN %s AND %s
                    ORDER BY fecha
                ''', [tag, fecha_inicio, fecha_fin])

                rows = cursor.fetchall()
                valores = [float(r[1]) for r in rows if r[1] is not None]
                fechas = [r[0].strftime('%Y-%m-%d %H:%M') for r in rows]

                resultado = {
                    'tag': tag,
                    'fechas': fechas,
                    'valores': valores,
                    'min': round(min(valores), 2) if valores else 0,
                    'max': round(max(valores), 2) if valores else 0,
                    'prom': round(sum(valores) / len(valores), 2) if valores else 0,
                }
                resultados.append(resultado)
        return resultados

    def agrupar_por_tag(metricas):
        agrupados = defaultdict(dict)
        for metrica in ['voltaje', 'amperaje', 'demanda']:
            for dato in metricas[metrica]:
                tag = dato['tag']
                agrupados[tag]['tag'] = tag
                agrupados[tag]['fechas'] = dato['fechas']
                agrupados[tag][metrica] = {
                    'valores': dato['valores'],
                    'min': dato['min'],
                    'max': dato['max'],
                    'prom': dato['prom']
                }
        return list(agrupados.values())

    metricas_comp = {
        'voltaje': get_metric_data(compresores, 'log_refrigeracion', 'voltaje'),
        'amperaje': get_metric_data(compresores, 'log_refrigeracion', 'amperaje'),
        'demanda': get_metric_data(compresores, 'log_refrigeracion', 'demanda_kw'),
    }

    metricas_tun = {
        'voltaje': get_metric_data(tuneles, 'log_refrigeracion', 'voltaje'),
        'amperaje': get_metric_data(tuneles, 'log_refrigeracion', 'amperaje'),
        'demanda': get_metric_data(tuneles, 'log_refrigeracion', 'demanda_kw'),
    }

    return JsonResponse({
        'compresores': agrupar_por_tag(metricas_comp),
        'tuneles': agrupar_por_tag(metricas_tun),
    }, safe=False)
