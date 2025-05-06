from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime, timedelta, timezone
import time



# ------------------ CONFIG ------------------
INFLUX_URL = "http://190.114.253.120:8086"
INFLUX_TOKEN = "IM2K2piXYPqLzkvlAcbqCBmnd_prmJdA6P09YY_TgHQF7PiuOhl8Q_wgReYwjljsIa3TnWVPd_8biKytMq9_GQ=="
ORG = "Ingero"
BUCKET_READ = "Prueba2"
BUCKET_WRITE = "Calculados"
MEASUREMENT = "sensor_data"
MINUTOS_RETROCESO = 5

# ------------------ FUNCIONES GENERALES ------------------

def get_first_and_last(query_api, equipo, campo, start_first, start_last, stop_last):
    query_first = f'''
from(bucket: "{BUCKET_READ}")
  |> range(start: time(v: "{start_first.isoformat()}"), stop: time(v: "{stop_last.isoformat()}"))
  |> filter(fn: (r) => r._measurement == "{MEASUREMENT}" and r._field == "{campo}" and r.equipo == "{equipo}")
  |> first()
'''
    query_last = f'''
from(bucket: "{BUCKET_READ}")
  |> range(start: time(v: "{start_last.isoformat()}"), stop: time(v: "{stop_last.isoformat()}"))
  |> filter(fn: (r) => r._measurement == "{MEASUREMENT}" and r._field == "{campo}" and r.equipo == "{equipo}")
  |> last()
'''

    first_val, last_val = 0.0, 0.0
    try:
        for t in query_api.query(org=ORG, query=query_first): 
            for r in t.records: first_val = float(r.get_value())
        for t in query_api.query(org=ORG, query=query_last):
            for r in t.records: last_val = float(r.get_value())
    except: pass

    return first_val, last_val

def get_first_and_last_by_topic(query_api, topic, campo, start_first, start_last, stop_last):
    query_first = f'''
from(bucket: "{BUCKET_READ}")
  |> range(start: time(v: "{start_first.isoformat()}"), stop: time(v: "{stop_last.isoformat()}"))
  |> filter(fn: (r) => r._measurement == "{MEASUREMENT}" and r._field == "{campo}" and r.topic == "{topic}")
  |> first()
'''
    query_last = f'''
from(bucket: "{BUCKET_READ}")
  |> range(start: time(v: "{start_last.isoformat()}"), stop: time(v: "{stop_last.isoformat()}"))
  |> filter(fn: (r) => r._measurement == "{MEASUREMENT}" and r._field == "{campo}" and r.topic == "{topic}")
  |> last()
'''
    first_val, last_val = 0.0, 0.0
    try:
        for t in query_api.query(org=ORG, query=query_first): 
            for r in t.records: first_val = float(r.get_value())
        for t in query_api.query(org=ORG, query=query_last):
            for r in t.records: last_val = float(r.get_value())
    except: pass
    return first_val, last_val

def get_last_valor(query_api, equipo, campo, start, stop, divisor=1.0):
    query = f'''
from(bucket: "{BUCKET_READ}")
  |> range(start: time(v: "{start.isoformat()}"), stop: time(v: "{stop.isoformat()}"))
  |> filter(fn: (r) => r._measurement == "{MEASUREMENT}" and r._field == "{campo}" and r.equipo == "{equipo}")
  |> last()
'''
    try:
        result = query_api.query(org=ORG, query=query)
        for table in result:
            for record in table.records:
                return float(record.get_value()) / divisor
    except:
        return 0.0
    return 0.0

def get_last_by_topic(query_api, topic, campo, start, stop, divisor=1.0):
    query = f'''
from(bucket: "{BUCKET_READ}")
  |> range(start: time(v: "{start.isoformat()}"), stop: time(v: "{stop.isoformat()}"))
  |> filter(fn: (r) => r._measurement == "{MEASUREMENT}" and r._field == "{campo}" and r.topic == "{topic}")
  |> last()
'''
    try:
        result = query_api.query(org=ORG, query=query)
        for table in result:
            for record in table.records:
                return float(record.get_value()) / divisor
    except:
        return 0.0
    return 0.0

# ------------------ CÁLCULOS POR MEDIDOR ------------------

def calcular_em39(query_api, inicio_mes, start, stop):
    total = sum([
        (get_first_and_last(query_api, eq, campo, inicio_mes, start, stop)[1] -
         get_first_and_last(query_api, eq, campo, inicio_mes, start, stop)[0]) / 10.0
        for eq, campo in [("EM1", "EAP1"), ("EM2", "EAP2"), ("EM5", "EAP5"), ("EM6", "EAP6")]
    ])
    return Point(MEASUREMENT).tag("equipo", "EM39").field("EAP39", total).time(stop, WritePrecision.NS)

def calcular_pat39(query_api, start, stop):
    total = sum([
        get_last_valor(query_api, eq, campo, start, stop, 1000.0)
        for eq, campo in [("EM1", "PAT1"), ("EM2", "PAT2"), ("EM5", "PAT5"), ("EM6", "PAT6")]
    ])
    return Point(MEASUREMENT).tag("equipo", "EM39").field("PAT39", total).time(stop, WritePrecision.NS)

def calcular_em40(query_api, inicio_mes, start, stop):
    f6, l6 = get_first_and_last(query_api, "EM6", "EAP6", inicio_mes, start, stop)
    f7, l7 = get_first_and_last(query_api, "EM7", "EAP7", inicio_mes, start, stop)
    f8, l8 = get_first_and_last(query_api, "EM8", "EAP8", inicio_mes, start, stop)
    total = (l6 - f6) / 10.0 - (l7 - f7) - (l8 - f8)
    return Point(MEASUREMENT).tag("equipo", "EM40").field("EAP40", total).time(stop, WritePrecision.NS)

def calcular_pat40(query_api, start, stop):
    total = (
        get_last_valor(query_api, "EM6", "PAT6", start, stop, 1000.0) -
        get_last_valor(query_api, "EM7", "PAT7", start, stop) -
        get_last_valor(query_api, "EM8", "PAT8", start, stop)
    )
    return Point(MEASUREMENT).tag("equipo", "EM40").field("PAT40", total).time(stop, WritePrecision.NS)

def calcular_em41(query_api, inicio_mes, start, stop):
    f1, l1 = get_first_and_last(query_api, "EM1", "EAP1", inicio_mes, start, stop)
    f2, l2 = get_first_and_last(query_api, "EM2", "EAP2", inicio_mes, start, stop)
    f3, l3 = get_first_and_last_by_topic(query_api, "/EM3", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    total = (l1 - f1 + l2 - f2 + l3 - f3) / 10.0
    return Point(MEASUREMENT).tag("equipo", "EM41").field("EAP41", total).time(stop, WritePrecision.NS)

def calcular_pat41(query_api, start, stop):
    total = (
        get_last_valor(query_api, "EM1", "PAT1", start, stop, 1000.0) +
        get_last_valor(query_api, "EM2", "PAT2", start, stop, 1000.0) +
        get_last_by_topic(query_api, "/EM3", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    )
    return Point(MEASUREMENT).tag("equipo", "EM41").field("PAT41", total).time(stop, WritePrecision.NS)

def calcular_eap43(query_api, inicio_mes, start, stop):
    f20, l20 = get_first_and_last_by_topic(query_api, "/PEM3_EM20", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f21, l21 = get_first_and_last_by_topic(query_api, "/PEM3_EM21", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    total = ((l20 - f20) + (l21 - f21)) / 10.0
    return Point(MEASUREMENT).tag("equipo", "EM43").field("EAP43", total).time(stop, WritePrecision.NS)

def calcular_pat43(query_api, start, stop):
    v20 = get_last_by_topic(query_api, "/PEM3_EM20", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v21 = get_last_by_topic(query_api, "/PEM3_EM21", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    total = v20 + v21
    return Point(MEASUREMENT).tag("equipo", "EM43").field("PAT43", total).time(stop, WritePrecision.NS)

def calcular_eap44(query_api, inicio_mes, start, stop):
    f18, l18 = get_first_and_last_by_topic(query_api, "/EM18", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f19, l19 = get_first_and_last_by_topic(query_api, "/EM19", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    v18 = (l18 - f18) / 10.0
    v19 = (l19 - f19) / 10.0
    total = v18 - v19

    return Point(MEASUREMENT).tag("equipo", "EM44").field("EAP44", total).time(stop, WritePrecision.NS)

def calcular_pat44(query_api, start, stop):
    v18 = get_last_by_topic(query_api, "/EM18", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v19 = get_last_by_topic(query_api, "/EM19", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    total = v18 - v19

    return Point(MEASUREMENT).tag("equipo", "EM44").field("PAT44", total).time(stop, WritePrecision.NS)

def calcular_eap45(query_api, inicio_mes, start, stop):
    f17, l17 = get_first_and_last_by_topic(query_api, "/EM17", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f29, l29 = get_first_and_last_by_topic(query_api, "/PEM6_EM29", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    v17 = (l17 - f17) / 10.0
    v29 = (l29 - f29)

    diferencia = v17 - v29
    valor_final = diferencia if diferencia > 40.0 else 0.0

    return Point(MEASUREMENT).tag("equipo", "EM45").field("EAP45", valor_final).time(stop, WritePrecision.NS)

def calcular_pat45(query_api, start, stop):
    v17 = get_last_by_topic(query_api, "/EM17", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v29 = get_last_by_topic(query_api, "/PEM6_EM29", "POTENCIA_ACTIVA_TOTAL", start, stop)

    diferencia = v17 - v29
    valor_final = diferencia if diferencia > 40.0 else 0.0

    return Point(MEASUREMENT).tag("equipo", "EM45").field("PAT45", valor_final).time(stop, WritePrecision.NS)

def calcular_eap49(query_api, inicio_mes, start, stop):
    f35, l35 = get_first_and_last_by_topic(query_api, "/PEM6_EM35", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f36, l36 = get_first_and_last_by_topic(query_api, "/PEM6_EM36", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    v35 = (l35 - f35)
    v36 = (l36 - f36)
    total = v35 + v36

    return Point(MEASUREMENT).tag("equipo", "EM49").field("EAP49", total).time(stop, WritePrecision.NS)

def calcular_pat49(query_api, start, stop):
    v35 = get_last_by_topic(query_api, "/PEM6_EM35", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v36 = get_last_by_topic(query_api, "/PEM6_EM36", "POTENCIA_ACTIVA_TOTAL", start, stop)

    total = (v35 if v35 else 0.0) + (v36 if v36 else 0.0)
    return Point(MEASUREMENT).tag("equipo", "EM49").field("PAT49", total).time(stop, WritePrecision.NS)


def calcular_eap50(query_api, inicio_mes, start, stop):
    f33, l33 = get_first_and_last_by_topic(query_api, "/EM33", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f35, l35 = get_first_and_last_by_topic(query_api, "/PEM6_EM35", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f36, l36 = get_first_and_last_by_topic(query_api, "/PEM6_EM36", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    v33 = (l33 - f33) / 10.0
    v35 = (l35 - f35)
    v36 = (l36 - f36)

    em49 = v35 + v36
    diferencia = v33 - em49
    resultado = diferencia if diferencia > 40.0 else 0.0

    return Point(MEASUREMENT).tag("equipo", "EM50").field("EAP50", resultado).time(stop, WritePrecision.NS)

def calcular_pat50(query_api, start, stop):
    v33 = get_last_by_topic(query_api, "/EM33", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v35 = get_last_by_topic(query_api, "/PEM6_EM35", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v36 = get_last_by_topic(query_api, "/PEM6_EM36", "POTENCIA_ACTIVA_TOTAL", start, stop)

    em49 = (v35 if v35 else 0.0) + (v36 if v36 else 0.0)
    diferencia = v33 - em49
    resultado = diferencia if diferencia > 40.0 else 0.0

    return Point(MEASUREMENT).tag("equipo", "EM50").field("PAT50", resultado).time(stop, WritePrecision.NS)


def calcular_eap42(query_api, inicio_mes, start, stop):
    f1, l1 = get_first_and_last(query_api, "EM1", "EAP1", inicio_mes, start, stop)
    f2, l2 = get_first_and_last(query_api, "EM2", "EAP2", inicio_mes, start, stop)
    f3, l3 = get_first_and_last_by_topic(query_api, "/EM3", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f5, l5 = get_first_and_last(query_api, "EM5", "EAP5", inicio_mes, start, stop)
    f6, l6 = get_first_and_last(query_api, "EM6", "EAP6", inicio_mes, start, stop)
    f7, l7 = get_first_and_last(query_api, "EM7", "EAP7", inicio_mes, start, stop)
    f8, l8 = get_first_and_last(query_api, "EM8", "EAP8", inicio_mes, start, stop)

    em1 = (l1 - f1) / 10.0
    em2 = (l2 - f2) / 10.0
    em3 = (l3 - f3) / 10.0
    em5 = (l5 - f5) / 10.0
    em6 = (l6 - f6) / 10.0
    em7 = (l7 - f7)
    em8 = (l8 - f8)

    total = (em1 + em2 + em3) + em5 + (em6 - em7 - em8)

    return Point(MEASUREMENT).tag("equipo", "EM42").field("EAP42", total).time(stop, WritePrecision.NS)

def calcular_pat42(query_api, start, stop):
    em1 = get_last_valor(query_api, "EM1", "PAT1", start, stop, 1000.0)
    em2 = get_last_valor(query_api, "EM2", "PAT2", start, stop, 1000.0)
    em3 = get_last_by_topic(query_api, "/EM3", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    em5 = get_last_valor(query_api, "EM5", "PAT5", start, stop, 1000.0)
    em6 = get_last_valor(query_api, "EM6", "PAT6", start, stop, 1000.0)
    em7 = get_last_valor(query_api, "EM7", "PAT7", start, stop)
    em8 = get_last_valor(query_api, "EM8", "PAT8", start, stop)

    total = (em1 + em2 + em3) + em5 + (em6 - em7 - em8)

    return Point(MEASUREMENT).tag("equipo", "EM42").field("PAT42", total).time(stop, WritePrecision.NS)

def calcular_eap46(query_api, inicio_mes, start, stop):
    f10, l10 = get_first_and_last_by_topic(query_api, "/PEM3_EM10", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f12, l12 = get_first_and_last_by_topic(query_api, "/PEM3_EM12", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f30, l30 = get_first_and_last_by_topic(query_api, "/PEM3_EM30", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f13, l13 = get_first_and_last_by_topic(query_api, "/PEM3_EM13", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f14, l14 = get_first_and_last_by_topic(query_api, "/PEM3_EM14", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f15, l15 = get_first_and_last_by_topic(query_api, "/PEM3_EM15", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f31, l31 = get_first_and_last_by_topic(query_api, "/EM31", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f32, l32 = get_first_and_last_by_topic(query_api, "/PEM3_EM32", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    em10 = (l10 - f10) / 10.0
    em12 = (l12 - f12)
    em30 = (l30 - f30) / 10.0
    em13 = (l13 - f13) / 10.0
    em14 = (l14 - f14) / 10.0
    em15 = (l15 - f15) / 10.0
    em31 = (l31 - f31) / 10.0
    em32 = (l32 - f32) / 10.0

    total = em10 + em12 + em30 + em13 + em14 + em15 + em31 + em32

    return Point(MEASUREMENT).tag("equipo", "EM46").field("EAP46", total).time(stop, WritePrecision.NS)

def calcular_pat46(query_api, start, stop):
    em10 = get_last_by_topic(query_api, "/PEM3_EM10", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    em12 = get_last_by_topic(query_api, "/PEM3_EM12", "POTENCIA_ACTIVA_TOTAL", start, stop)  # sin divisor
    em30 = get_last_by_topic(query_api, "/PEM3_EM30", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    em13 = get_last_by_topic(query_api, "/PEM3_EM13", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    em14 = get_last_by_topic(query_api, "/PEM3_EM14", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    em15 = get_last_by_topic(query_api, "/PEM3_EM15", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    em31 = get_last_by_topic(query_api, "/EM31", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    em32 = get_last_by_topic(query_api, "/PEM3_EM32", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)

    total = em10 + em12 + em30 + em13 + em14 + em15 + em31 + em32

    return Point(MEASUREMENT).tag("equipo", "EM46").field("PAT46", total).time(stop, WritePrecision.NS)


def calcular_eap47(query_api, inicio_mes, start, stop):
    f25, l25 = get_first_and_last(query_api, "EM25", "EAP25", inicio_mes, start, stop)
    f26, l26 = get_first_and_last(query_api, "EM26", "EAP26", inicio_mes, start, stop)
    f27, l27 = get_first_and_last(query_api, "EM27", "EAP27", inicio_mes, start, stop)
    f28, l28 = get_first_and_last(query_api, "EM28", "EAP28", inicio_mes, start, stop)
    f29, l29 = get_first_and_last_by_topic(query_api, "/PEM6_EM29", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f35, l35 = get_first_and_last_by_topic(query_api, "/PEM6_EM35", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f36, l36 = get_first_and_last_by_topic(query_api, "/PEM6_EM36", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f37, l37 = get_first_and_last_by_topic(query_api, "/PEM6_EM37", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f38, l38 = get_first_and_last_by_topic(query_api, "/PEM6_EM38", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f33, l33 = get_first_and_last_by_topic(query_api, "/EM33", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f17, l17 = get_first_and_last_by_topic(query_api, "/EM17", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    # Directos
    em25 = l25 - f25
    em26 = l26 - f26
    em27 = l27 - f27
    em28 = l28 - f28
    em29 = l29 - f29
    em37 = l37 - f37
    em38 = l38 - f38

    # EM49 = EM35 + EM36
    em49 = (l35 - f35) + (l36 - f36)

    # EM45 = (EM17 - EM29) > 40.0
    delta_45 = (l17 - f17) - em29
    em45 = delta_45 if delta_45 > 40.0 else 0.0

    # EM50 = (EM33 - EM49) > 40.0
    delta_50 = ((l33 - f33) / 10.0) - em49
    em50 = delta_50 if delta_50 > 40.0 else 0.0

    total = em25 + em26 + em27 + em28 + em29 + em37 + em38 + em49 + em45 + em50

    return Point(MEASUREMENT).tag("equipo", "EM47").field("EAP47", total).time(stop, WritePrecision.NS)

def calcular_pat47(query_api, start, stop):
    v25 = get_last_valor(query_api, "EM25", "PAT25", start, stop)
    v26 = get_last_valor(query_api, "EM26", "PAT26", start, stop)
    v27 = get_last_valor(query_api, "EM27", "PAT27", start, stop)
    v28 = get_last_valor(query_api, "EM28", "PAT28", start, stop)
    v29 = get_last_by_topic(query_api, "/PEM6_EM29", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v35 = get_last_by_topic(query_api, "/PEM6_EM35", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v36 = get_last_by_topic(query_api, "/PEM6_EM36", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v37 = get_last_by_topic(query_api, "/PEM6_EM37", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v38 = get_last_by_topic(query_api, "/PEM6_EM38", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v17 = get_last_by_topic(query_api, "/EM17", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v33 = get_last_by_topic(query_api, "/EM33", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)

    # EM49 y condiciones
    em49 = v35 + v36
    em45 = (v17 - v29) if (v17 - v29) > 40.0 else 0.0
    em50 = (v33 - em49) if (v33 - em49) > 40.0 else 0.0

    total = v25 + v26 + v27 + v28 + v29 + v35 + v36 + v37 + v38 + em45 + em50

    return Point(MEASUREMENT).tag("equipo", "EM47").field("PAT47", total).time(stop, WritePrecision.NS)


def calcular_eap48(query_api, inicio_mes, start, stop):
    f20, l20 = get_first_and_last_by_topic(query_api, "/PEM3_EM20", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f21, l21 = get_first_and_last_by_topic(query_api, "/PEM3_EM21", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f34, l34 = get_first_and_last_by_topic(query_api, "/PEM3_EM34", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f18, l18 = get_first_and_last_by_topic(query_api, "/EM18", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    v20 = (l20 - f20) / 10.0
    v21 = (l21 - f21) / 10.0
    v34 = (l34 - f34)
    v18 = (l18 - f18) / 10.0

    total = v20 + v21 + v34 - v18

    return Point(MEASUREMENT).tag("equipo", "EM48").field("EAP48", total).time(stop, WritePrecision.NS)

def calcular_pat48(query_api, start, stop):
    v20 = get_last_by_topic(query_api, "/PEM3_EM20", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v21 = get_last_by_topic(query_api, "/PEM3_EM21", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v34 = get_last_by_topic(query_api, "/PEM3_EM34", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v18 = get_last_by_topic(query_api, "/EM18", "PAT", start, stop, 1000.0)

    total = v20 + v21 + v34 - v18

    return Point(MEASUREMENT).tag("equipo", "EM48").field("PAT48", total).time(stop, WritePrecision.NS)

def calcular_eap52(query_api, inicio_mes, start, stop):
    f7, l7 = get_first_and_last(query_api, "EM7", "EAP7", inicio_mes, start, stop)
    f19, l19 = get_first_and_last_by_topic(query_api, "/EM19", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    v7 = l7 - f7  # sin división
    v19 = (l19 - f19) / 10.0

    total = v7 + v19
    return Point(MEASUREMENT).tag("equipo", "EM52").field("EAP52", total).time(stop, WritePrecision.NS)

def calcular_pat52(query_api, start, stop):
    v7 = get_last_valor(query_api, "EM7", "PAT7", start, stop)  # sin dividir
    v19 = get_last_by_topic(query_api, "/EM19", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)

    total = v7 + v19
    return Point(MEASUREMENT).tag("equipo", "EM52").field("PAT52", total).time(stop, WritePrecision.NS)

def calcular_eap53(query_api, inicio_mes, start, stop):
    f1, l1 = get_first_and_last(query_api, "EM1", "EAP1", inicio_mes, start, stop)
    f2, l2 = get_first_and_last(query_api, "EM2", "EAP2", inicio_mes, start, stop)
    f3, l3 = get_first_and_last_by_topic(query_api, "/EM3", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f5, l5 = get_first_and_last(query_api, "EM5", "EAP5", inicio_mes, start, stop)
    f18, l18 = get_first_and_last_by_topic(query_api, "/EM18", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f19, l19 = get_first_and_last_by_topic(query_api, "/EM19", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    total = (
        (l1 - f1) + (l2 - f2) + (l3 - f3) + (l5 - f5) - (l18 - f18) + (l19 - f19)
    ) / 10.0

    return Point(MEASUREMENT).tag("equipo", "EM53").field("EAP53", total).time(stop, WritePrecision.NS)

def calcular_pat53(query_api, start, stop):
    v1 = get_last_valor(query_api, "EM1", "PAT1", start, stop, 1000.0)
    v2 = get_last_valor(query_api, "EM2", "PAT2", start, stop, 1000.0)
    v3 = get_last_by_topic(query_api, "/EM3", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v5 = get_last_valor(query_api, "EM5", "PAT5", start, stop, 1000.0)
    v18 = get_last_by_topic(query_api, "/EM18", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v19 = get_last_by_topic(query_api, "/EM19", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)

    total = v1 + v2 + v3 + v5 - v18 + v19

    return Point(MEASUREMENT).tag("equipo", "EM53").field("PAT53", total).time(stop, WritePrecision.NS)

def calcular_eap54(query_api, inicio_mes, start, stop):
    # --- EM48 ---
    f20, l20 = get_first_and_last_by_topic(query_api, "/PEM3_EM20", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f21, l21 = get_first_and_last_by_topic(query_api, "/PEM3_EM21", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f34, l34 = get_first_and_last_by_topic(query_api, "/PEM3_EM34", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f18, l18 = get_first_and_last_by_topic(query_api, "/EM18", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    em48 = ((l20 - f20) + (l21 - f21)) / 10.0 + (l34 - f34) - (l18 - f18) / 10.0

    # --- EM46 ---
    topics_em46 = [
        ("/PEM3_EM10", True), ("/PEM3_EM12", False), ("/PEM3_EM30", True),
        ("/PEM3_EM13", True), ("/PEM3_EM14", True), ("/PEM3_EM15", True),
        ("/EM31", True), ("/PEM3_EM32", True)
    ]
    em46 = 0.0
    for topic, dividir in topics_em46:
        f, l = get_first_and_last_by_topic(query_api, topic, "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
        em46 += (l - f) / (10.0 if dividir else 1.0)

    # --- EM47 ---
    # Ya fue calculado como: EM25+26+...+EM38 + EM45 + EM50
    # Volvemos a calcular EM45 y EM50 para sumar junto con EM25-EM38

    em47_total = 0.0
    for equipo, campo, dividir in [
        ("EM25", "EAP25", False), ("EM26", "EAP26", False), ("EM27", "EAP27", False),
        ("EM28", "EAP28", False)
    ]:
        f, l = get_first_and_last(query_api, equipo, campo, inicio_mes, start, stop)
        em47_total += (l - f) / (10.0 if dividir else 1.0)

    for topic in ["/PEM6_EM29", "/PEM6_EM35", "/PEM6_EM36", "/PEM6_EM37", "/PEM6_EM38"]:
        f, l = get_first_and_last_by_topic(query_api, topic, "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
        em47_total += (l - f)

    # EM45
    f17, l17 = get_first_and_last_by_topic(query_api, "/EM17", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f29, l29 = get_first_and_last_by_topic(query_api, "/PEM6_EM29", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    diff45 = (l17 - f17) / 10.0 - (l29 - f29)
    em45 = diff45 if diff45 > 40.0 else 0.0
    em47_total += em45

    # EM50
    f33, l33 = get_first_and_last_by_topic(query_api, "/EM33", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f35, l35 = get_first_and_last_by_topic(query_api, "/PEM6_EM35", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f36, l36 = get_first_and_last_by_topic(query_api, "/PEM6_EM36", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    em49 = (l35 - f35) + (l36 - f36)
    diff50 = (l33 - f33) / 10.0 - em49
    em50 = diff50 if diff50 > 40.0 else 0.0
    em47_total += em50

    # --- EM22 ---
    f22, l22 = get_first_and_last(query_api, "EM22", "EAP22", inicio_mes, start, stop)
    em22 = (l22 - f22) / 10.0

    # --- Resultado final ---
    total = em48 - em46 - em47_total - em22
    return Point(MEASUREMENT).tag("equipo", "EM54").field("EAP54", total).time(stop, WritePrecision.NS)

def calcular_pat54(query_api, start, stop):
    # EM48
    v20 = get_last_by_topic(query_api, "/PEM3_EM20", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v21 = get_last_by_topic(query_api, "/PEM3_EM21", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v34 = get_last_by_topic(query_api, "/PEM3_EM34", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v18 = get_last_by_topic(query_api, "/EM18", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    em48 = v20 + v21 + v34 - v18

    # EM46
    em46 = 0.0
    for topic, dividir in [
        ("/PEM3_EM10", True), ("/PEM3_EM12", False), ("/PEM3_EM30", True),
        ("/PEM3_EM13", True), ("/PEM3_EM14", True), ("/PEM3_EM15", True),
        ("/EM31", True), ("/PEM3_EM32", True)
    ]:
        em46 += get_last_by_topic(query_api, topic, "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0 if dividir else 1.0)

    # EM22
    em22 = get_last_valor(query_api, "EM22", "PAT22", start, stop, 1000.0)

    # EM47
    em47 = 0.0
    for equipo, campo, dividir in [
        ("EM25", "PAT25", False), ("EM26", "PAT26", False), ("EM27", "PAT27", False), ("EM28", "PAT28", False)
    ]:
        em47 += get_last_valor(query_api, equipo, campo, start, stop, 1000.0 if dividir else 1.0)

    for topic in ["/PEM6_EM29", "/PEM6_EM35", "/PEM6_EM36", "/PEM6_EM37", "/PEM6_EM38"]:
        em47 += get_last_by_topic(query_api, topic, "POTENCIA_ACTIVA_TOTAL", start, stop)

    # EM45
    v17 = get_last_by_topic(query_api, "/EM17", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v29 = get_last_by_topic(query_api, "/PEM6_EM29", "POTENCIA_ACTIVA_TOTAL", start, stop)
    diff45 = v17 - v29
    em45 = diff45 if diff45 > 40.0 else 0.0
    em47 += em45

    # EM50
    v33 = get_last_by_topic(query_api, "/EM33", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v35 = get_last_by_topic(query_api, "/PEM6_EM35", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v36 = get_last_by_topic(query_api, "/PEM6_EM36", "POTENCIA_ACTIVA_TOTAL", start, stop)
    diff50 = v33 - (v35 + v36)
    em50 = diff50 if diff50 > 40.0 else 0.0
    em47 += em50

    total = em48 - em46 - em47 - em22
    return Point(MEASUREMENT).tag("equipo", "EM54").field("PAT54", total).time(stop, WritePrecision.NS)

def calcular_eap56(query_api, inicio_mes, start, stop):
    f17, l17 = get_first_and_last_by_topic(query_api, "/EM17", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f29, l29 = get_first_and_last_by_topic(query_api, "/PEM6_EM29", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    diff = (l17 - f17) / 10.0 - (l29 - f29)
    resultado = diff if diff <= 40.0 else 0.0

    return Point(MEASUREMENT).tag("equipo", "EM56").field("EAP56", resultado).time(stop, WritePrecision.NS)


def calcular_pat56(query_api, start, stop):
    v17 = get_last_by_topic(query_api, "/EM17", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v29 = get_last_by_topic(query_api, "/PEM6_EM29", "POTENCIA_ACTIVA_TOTAL", start, stop)
    diff = v17 - v29
    resultado = diff if diff <= 40.0 else 0.0
    return Point(MEASUREMENT).tag("equipo", "EM56").field("PAT56", resultado).time(stop, WritePrecision.NS)

def calcular_eap57(query_api, inicio_mes, start, stop):
    f33, l33 = get_first_and_last_by_topic(query_api, "/EM33", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f35, l35 = get_first_and_last_by_topic(query_api, "/PEM6_EM35", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)
    f36, l36 = get_first_and_last_by_topic(query_api, "/PEM6_EM36", "ENERGIA_ACTIVA_POSITIVA", inicio_mes, start, stop)

    em33 = (l33 - f33) / 10.0
    em49 = (l35 - f35) + (l36 - f36)

    diff = em33 - em49
    resultado = diff if diff <= 40.0 else 0.0

    return Point(MEASUREMENT).tag("equipo", "EM57").field("EAP57", resultado).time(stop, WritePrecision.NS)


def calcular_pat57(query_api, start, stop):
    v33 = get_last_by_topic(query_api, "/EM33", "POTENCIA_ACTIVA_TOTAL", start, stop, 1000.0)
    v35 = get_last_by_topic(query_api, "/PEM6_EM35", "POTENCIA_ACTIVA_TOTAL", start, stop)
    v36 = get_last_by_topic(query_api, "/PEM6_EM36", "POTENCIA_ACTIVA_TOTAL", start, stop)
    diff = v33 - (v35 + v36)
    resultado = diff if diff <= 40.0 else 0.0
    return Point(MEASUREMENT).tag("equipo", "EM57").field("PAT57", resultado).time(stop, WritePrecision.NS)


# ------------------ MAIN ------------------

def main():
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
    query_api = client.query_api()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    now = datetime.utcnow().replace(tzinfo=timezone.utc, second=0, microsecond=0)
    inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    for i in range(MINUTOS_RETROCESO, 0, -1):
        start = now - timedelta(minutes=i)
        stop = start + timedelta(minutes=1)
        print(f"\n🕒 Ventana: {start.strftime('%Y-%m-%d %H:%M')}")

        try:
            puntos = [
                calcular_em39(query_api, inicio_mes, start, stop),
                calcular_pat39(query_api, start, stop),
                calcular_em40(query_api, inicio_mes, start, stop),
                calcular_pat40(query_api, start, stop),
                calcular_em41(query_api, inicio_mes, start, stop),
                calcular_pat41(query_api, start, stop),
                calcular_eap43(query_api, inicio_mes, start, stop),
                calcular_pat43(query_api, start, stop),
                calcular_eap44(query_api, inicio_mes, start, stop),
                calcular_pat44(query_api, start, stop),
                calcular_eap45(query_api, inicio_mes, start, stop),
                calcular_pat45(query_api, start, stop),
                calcular_eap49(query_api, inicio_mes, start, stop),
                calcular_pat49(query_api, start, stop),
                calcular_eap50(query_api, inicio_mes, start, stop),
                calcular_pat50(query_api, start, stop),
                calcular_eap42(query_api, inicio_mes, start, stop),
                calcular_pat42(query_api, start, stop),
                calcular_eap46(query_api, inicio_mes, start, stop),
                calcular_pat46(query_api, start, stop),
                calcular_eap47(query_api, inicio_mes, start, stop),
                calcular_pat47(query_api, start, stop),
                calcular_eap48(query_api, inicio_mes, start, stop),
                calcular_pat48(query_api, start, stop),
                calcular_eap52(query_api, inicio_mes, start, stop),
                calcular_pat52(query_api, start, stop),
                calcular_eap53(query_api, inicio_mes, start, stop),
                calcular_pat53(query_api, start, stop),
                calcular_eap54(query_api, inicio_mes, start, stop),
                calcular_pat54(query_api, start, stop),
                calcular_eap56(query_api, inicio_mes, start, stop),
                calcular_pat56(query_api, start, stop),
                calcular_eap57(query_api, inicio_mes, start, stop),
                calcular_pat57(query_api, start, stop)

            ]
            write_api.write(bucket=BUCKET_WRITE, org=ORG, record=puntos)
            print(f"✅ EM39–EM54 procesados correctamente para {stop.strftime('%H:%M')}")
        except Exception as e:
            print(f"❌ Error general: {e}")

    client.close()

if __name__ == "__main__":
    print("\n🔄 Ejecutando cálculos EM39–EM54...")
    main()
    print("✅ Proceso finalizado.")