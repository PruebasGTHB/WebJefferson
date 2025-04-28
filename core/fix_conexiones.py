from core.models import ConexionMedidores, MedidorPosicion


def reparar_conexiones_huérfanas(eliminar_irrecuperables=True):
    errores = 0
    reparadas = 0
    eliminadas = 0

    conexiones = ConexionMedidores.objects.filter(
        origen__isnull=True
    ) | ConexionMedidores.objects.filter(
        destino__isnull=True
    )

    for conn in conexiones.distinct():
        try:
            if not conn.origen:
                conn.origen = MedidorPosicion.objects.get(
                    medidor_id=conn.origen_id)
            if not conn.destino:
                conn.destino = MedidorPosicion.objects.get(
                    medidor_id=conn.destino_id)

            conn.save()
            reparadas += 1

        except MedidorPosicion.DoesNotExist:
            errores += 1
            print(
                f"⚠️ No se encontró medidor '{conn.origen_id}' o '{conn.destino_id}' para conexión ID {conn.id}")

            if eliminar_irrecuperables:
                conn.delete()
                eliminadas += 1
                print(f"🗑️ Conexión ID {conn.id} eliminada")

    print("\n🎯 RESULTADOS:")
    print(f"✅ Conexiones reparadas: {reparadas}")
    print(f"❌ Con errores (medidor no encontrado): {errores}")
    if eliminar_irrecuperables:
        print(f"🗑️ Conexiones eliminadas: {eliminadas}")


# ELIMINAR CONEXIONES

# Repara las conexiones huérfanas asignando relaciones ForeignKey.

# Elimina automáticamente las conexiones donde no se encuentra el medidor_id correspondiente.

# Imprime un resumen claro al final.


# python manage.py shell

# from core.fix_conexiones import reparar_conexiones_huérfanas
# reparar_conexiones_huérfanas()
