from models.Lugares import Lugares
from models.Direcciones import Direcciones
from models.Georeferencia import Georeferencia
from sqlmodel import Session, select

def insertar_datos(df, session: Session):
    for fila in df.itertuples(index=False):
        # Verificar si el lugar ya existe para evitar duplicados
        stmt = select(Lugares).where(Lugares.nombre == fila.nombre)
        lugar = session.exec(stmt).first()
      

        if not lugar:
            lugar = Lugares(
                nombre=fila.nombre,
                fecha_registro=getattr(fila, "fecha_registro", None))
            session.add(lugar)
            session.flush()  # para obtener lugar.id

        # Crear y agregar dirección asociada
        direccion = Direcciones(
            direccion=fila.direccion,
            ciudad=getattr(fila, "ciudad", "Desconocido"),
            estado=getattr(fila, "estado", "Desconocido"),
            provincia=getattr(fila, "provincia", "Desconocido"),
            pais=getattr(fila, "pais", "Desconocido"),
            lugar=lugar
        )
        session.add(direccion)

        # Crear y agregar georeferencia asociada
        georeferencia = Georeferencia(
            latitud=fila.latitud,
            longitud=fila.longitud,
            lugar=lugar
        )
        session.add(georeferencia)

    session.commit()
    print("✅ Datos insertados correctamente.")