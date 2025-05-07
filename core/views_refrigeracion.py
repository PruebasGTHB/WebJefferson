from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from influxdb_client import InfluxDBClient
from django.conf import settings
import pytz
import traceback

ZONA_LOCAL = pytz.timezone(settings.INFLUXDB_ZONE)

@csrf_exempt
def datos_refrigeracion(request):
    try:
        inicio = request.GET.get("inicio", "2025-01-01")
        fin = request.GET.get("fin", "2025-01-31")

        compresores = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]
        tuneles = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10"]
        campos = {
            "voltaje": "VOLTAJE_FASES_PROMEDIO",
            "amperaje": "CORRIENTE_PROMEDIO",
            "demanda": "POTENCIA_ACTIVA_TOTAL"
        }

        def metricas_por_tag(bucket, tag_key, tags, field):
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
                      |> filter(fn: (r) =>
                        r._measurement == "sensor_data" and
                        r["_field"] == "{field}" and
                        r["{tag_key}"] == "{tag}"
                      )
                      |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
                    '''
                    tables = query_api.query(query)
                    fechas = []
                    valores = []
                    for table in tables:
                        for record in table.records:
                            local_time = record.get_time().astimezone(ZONA_LOCAL).strftime("%Y-%m-%d %H:%M")
                            fechas.append(local_time)
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

        def grafico_por_pivot(bucket, tag_key, field):
            from pandas import DataFrame
            query = f'''
            from(bucket: "{bucket}")
              |> range(start: time(v: "{inicio}T00:00:00Z"), stop: time(v: "{fin}T23:59:59Z"))
              |> filter(fn: (r) =>
                r._measurement == "sensor_data" and
                r._field == "{field}"
              )
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
            series = []
            for col in columnas:
                valores = df[col].tolist()
                if all(v is None for v in valores):
                    continue
                series.append({"nombre": col, "valores": valores})

            return {"fechas": fechas, "series": series}

        metricas_comp = {
            "voltaje": metricas_por_tag("Compresores", "topic", compresores, campos["voltaje"]),
            "amperaje": metricas_por_tag("Compresores", "topic", compresores, campos["amperaje"]),
            "demanda": metricas_por_tag("Compresores", "topic", compresores, campos["demanda"]),
        }

        metricas_tun = {
            "voltaje": metricas_por_tag("Tuneles", "TAG", tuneles, campos["voltaje"]),
            "amperaje": metricas_por_tag("Tuneles", "TAG", tuneles, campos["amperaje"]),
            "demanda": metricas_por_tag("Tuneles", "TAG", tuneles, campos["demanda"]),
        }

        return JsonResponse({
            "compresores": metricas_comp,
            "tuneles": metricas_tun,
            "grafico_voltaje_compresores": grafico_por_pivot("Compresores", "topic", campos["voltaje"]),
            "grafico_amperaje_compresores": grafico_por_pivot("Compresores", "topic", campos["amperaje"]),
            "grafico_demanda_compresores": grafico_por_pivot("Compresores", "topic", campos["demanda"]),
            "grafico_voltaje_tuneles": grafico_por_pivot("Tuneles", "TAG", campos["voltaje"]),
            "grafico_amperaje_tuneles": grafico_por_pivot("Tuneles", "TAG", campos["amperaje"]),
            "grafico_demanda_tuneles": grafico_por_pivot("Tuneles", "TAG", campos["demanda"]),
        }, safe=False)

    except Exception as e:
        print("❌ Error en datos_refrigeracion:", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)
