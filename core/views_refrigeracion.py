from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from influxdb_client import InfluxDBClient
from openpyxl import Workbook
from django.conf import settings
from datetime import datetime
import pytz
import traceback

ZONA_LOCAL = pytz.timezone(settings.INFLUXDB_ZONE)

# ----------------------------
# MÉTRICAS PRINCIPALES
# ----------------------------
METRICAS = {
    "voltaje": "VOLTAJE_FASES_PROMEDIO",
    "amperaje": "CORRIENTE_PROMEDIO",
    "demanda": "POTENCIA_ACTIVA_TOTAL"
}

COMPRESORES = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]
TUNELES = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"]

# ----------------------------
# UTILIDAD: QUERY AGRUPADA
# ----------------------------
def metricas_por_tag(bucket, tag_key, tags, field, inicio, fin):
    resultados = []
    with InfluxDBClient(
        url=settings.INFLUXDB_URL,
        token=settings.INFLUXDB_TOKEN,
        org=settings.INFLUXDB_ORG
    ) as client:
        query_api = client.query_api()
        for tag in tags:
            query = f'''
                from(bucket: "{bucket}")
                |> range(start: time(v: "{inicio}T00:00:00Z"), stop: time(v: "{fin}T23:59:59Z"))
                |> filter(fn: (r) => r._measurement == "sensor_data" and r._field == "{field}" and r["{tag_key}"] == "{tag}")
                |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
            '''
            tables = query_api.query(query)
            fechas, valores = [], []
            for table in tables:
                for record in table.records:
                    fechas.append(record.get_time().astimezone(ZONA_LOCAL).strftime("%Y-%m-%d %H:%M"))
                    valores.append(record.get_value())
            if valores:
                resultados.append({
                    "tag": tag,
                    "fechas": fechas,
                    "valores": valores,
                    "min": round(min(valores), 2),
                    "max": round(max(valores), 2),
                    "prom": round(sum(valores) / len(valores), 2)
                })
    return resultados

def grafico_por_pivot(bucket, tag_key, field, inicio, fin):
    from pandas import DataFrame
    query = f'''
        from(bucket: "{bucket}")
        |> range(start: time(v: "{inicio}T00:00:00Z"), stop: time(v: "{fin}T23:59:59Z"))
        |> filter(fn: (r) => r._measurement == "sensor_data" and r._field == "{field}")
        |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
        |> pivot(rowKey: ["_time"], columnKey: ["{tag_key}"], valueColumn: "_value")
    '''
    with InfluxDBClient(
        url=settings.INFLUXDB_URL,
        token=settings.INFLUXDB_TOKEN,
        org=settings.INFLUXDB_ORG
    ) as client:
        df = client.query_api().query_data_frame(query)

    if df.empty:
        return {"fechas": [], "series": []}

    df["_time"] = df["_time"].dt.tz_convert(ZONA_LOCAL)
    fechas = df["_time"].dt.strftime("%Y-%m-%d %H:%M").tolist()

    columnas = [col for col in df.columns if col not in ["_start", "_stop", "_time", "result", "table"]]
    series = [{"nombre": col, "valores": df[col].tolist()} for col in columnas if not df[col].isna().all()]
    return {"fechas": fechas, "series": series}

# ----------------------------
# VISTA PRINCIPAL
# ----------------------------
@csrf_exempt
def datos_refrigeracion(request):
    try:
        inicio = request.GET.get("inicio", "2025-01-01")
        fin = request.GET.get("fin", "2025-01-31")

        metricas_comp = {k: metricas_por_tag("Compresores", "topic", COMPRESORES, v, inicio, fin) for k, v in METRICAS.items()}
        metricas_tun = {k: metricas_por_tag("Tuneles", "TAG", TUNELES, v, inicio, fin) for k, v in METRICAS.items()}

        return JsonResponse({
            "compresores": metricas_comp,
            "tuneles": metricas_tun,
            "grafico_voltaje_compresores": grafico_por_pivot("Compresores", "topic", METRICAS["voltaje"], inicio, fin),
            "grafico_amperaje_compresores": grafico_por_pivot("Compresores", "topic", METRICAS["amperaje"], inicio, fin),
            "grafico_demanda_compresores": grafico_por_pivot("Compresores", "topic", METRICAS["demanda"], inicio, fin),
            "grafico_voltaje_tuneles": grafico_por_pivot("Tuneles", "TAG", METRICAS["voltaje"], inicio, fin),
            "grafico_amperaje_tuneles": grafico_por_pivot("Tuneles", "TAG", METRICAS["amperaje"], inicio, fin),
            "grafico_demanda_tuneles": grafico_por_pivot("Tuneles", "TAG", METRICAS["demanda"], inicio, fin)
        })
    except Exception as e:
        print("❌ Error en datos_refrigeracion:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)

# ----------------------------
# ÚLTIMA POTENCIA ACTUAL
# ----------------------------
@require_GET
def ultima_potencia(request):
    try:
        elementos = request.GET.getlist("tags[]")
        if not elementos:
            return JsonResponse({"error": "No se proporcionaron tags."}, status=400)

        resultados = {}
        with InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG
        ) as client:
            query_api = client.query_api()
            for tag in elementos:
                bucket, tag_key = ("Compresores", "topic") if tag.startswith("C") else ("Tuneles", "TAG") if tag.startswith("T") else (None, None)
                if not bucket:
                    continue
                query = f'''
                    from(bucket: "{bucket}")
                    |> range(start: -2h)
                    |> filter(fn: (r) => r._measurement == "sensor_data" and r._field == "POTENCIA_ACTIVA_TOTAL" and r["{tag_key}"] == "{tag}")
                    |> last()
                '''
                tables = query_api.query(query)
                for table in tables:
                    for record in table.records:
                        resultados[tag] = round(record.get_value(), 2)

        return JsonResponse(resultados)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ----------------------------
# EXPORTACIÓN DE EXCEL
# ----------------------------
@csrf_exempt
def descargar_datos(request):
    try:
        inicio = request.GET.get("inicio", "2025-01-01")
        fin = request.GET.get("fin", "2025-01-31")
        zona = pytz.timezone(settings.INFLUXDB_ZONE)

        equipos = {
            "Compresores": ("topic", COMPRESORES),
            "Tuneles": ("TAG", TUNELES)
        }

        wb = Workbook()
        wb.remove(wb.active)

        with InfluxDBClient(url=settings.INFLUXDB_URL, token=settings.INFLUXDB_TOKEN, org=settings.INFLUXDB_ORG) as client:
            query_api = client.query_api()
            for tipo, (tag_key, tags) in equipos.items():
                datos_ws = wb.create_sheet(title=f"{tipo} - Datos")
                resumen_ws = wb.create_sheet(title=f"{tipo} - Resumen")
                datos_ws.append(["Tag", "Métrica", "Fecha", "Valor"])
                resumen_ws.append(["Tag", "Métrica", "Mínimo", "Máximo", "Promedio"])

                for nombre, campo in METRICAS.items():
                    for tag in tags:
                        query = f'''
                            from(bucket: "{tipo}")
                            |> range(start: time(v: "{inicio}T00:00:00Z"), stop: time(v: "{fin}T23:59:59Z"))
                            |> filter(fn: (r) => r._measurement == "sensor_data" and r._field == "{campo}" and r["{tag_key}"] == "{tag}")
                            |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
                        '''
                        result = query_api.query(query)
                        valores = []
                        for table in result:
                            for record in table.records:
                                local_time = record.get_time().astimezone(zona).strftime("%Y-%m-%d %H:%M")
                                val = round(record.get_value(), 2)
                                valores.append(val)
                                datos_ws.append([tag, nombre, local_time, val])
                        if valores:
                            resumen_ws.append([
                                tag, nombre,
                                round(min(valores), 2),
                                round(max(valores), 2),
                                round(sum(valores) / len(valores), 2)
                            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        filename = f"datos_refrigeracion_{inicio}_a_{fin}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response

    except Exception as e:
        print("❌ Error en descargar_datos:", traceback.format_exc())
        return HttpResponse(f"Error al generar Excel: {str(e)}", status=500)

