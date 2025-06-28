import os
import time
from database import engine  # Importa el engine global
from sqlmodel import create_engine
from fastapi.responses import JSONResponse
from fastapi import APIRouter,UploadFile, File,FastAPI,Depends,Request  
from fastapi.responses import RedirectResponse,HTMLResponse
import pandas as pd
from io import BytesIO
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session,select
from database import get_session
from script.insert import insertar_datos
from models.Lugares import Lugares
from models.Direcciones import Direcciones
from models.Georeferencia import Georeferencia
from fastapi.responses import FileResponse
from database import engine, create_db_and_tables
app = FastAPI() 

# Mount static files directory for serving static content like CSS, JS, images, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.globals["zip"] = zip  # 👈 Esto expone zip a los templates


router = APIRouter()


import unicodedata
import re

def normalizar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        return "Desconocido"
    texto = texto.strip()
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = re.sub(r"[^\w\s,\-]", "", texto)  # ← ¡Comas incluidas!
    return texto.title()

@router.get("/datos/", response_class=HTMLResponse)
async def get_data(request:Request, session: Session = Depends(get_session)):
    lugares = session.exec(select(Lugares)).all()
    direcciones = session.exec(select(Direcciones)).all()
    georeferencias = session.exec(select(Georeferencia)).all()

    return templates.TemplateResponse("datos.html", {
        "request": request,
        "lugares": lugares,
        "direcciones": direcciones,
        "georeferencias": georeferencias
    })


def segmentar_direccion(direccion: str):
    partes = [p.strip() for p in direccion.split(",")]
    pais = partes[-1] if len(partes) >= 1 else "Desconocido"
    provincia = partes[-2] if len(partes) >= 2 else "Desconocido"
    estado = partes[-3] if len(partes) >= 3 else "Desconocido"
    ciudad = partes[-4] if len(partes) >= 4 else "Desconocido"
    return pd.Series([ciudad, estado, provincia, pais])



@router.post("/transform/")
async def transform(file:UploadFile = File(...),session: Session = Depends(get_session)):
    filename = file.filename.lower()
    print("Archivo recibido:", filename)
    if not filename.endswith(('.csv', '.txt', '.xls', '.xlsx')):
        return {"error": "File must be a CSV .txt, .xls, .xlsx"}
    
        
  # 1. Leer archivo
    content = await file.read()
    df = pd.read_csv(BytesIO(content), encoding='utf-8', sep=";", on_bad_lines='skip')

   # Si solo hay una columna, asúmela como "Nombre del lugar"
    if len(df.columns) == 1:
        col = df.columns[0]
        df = df.rename(columns={col: "nombre"})
        df["direccion"] = "Desconocido"
        df["georeferencia"] = "0.0,0.0"
        df["fecha_registro"] = pd.Timestamp.utcnow()
    else:
        columnas_requeridas = {"Nombre del lugar", "Dirección Completa", "Georeferencia"}
        columnas_archivo = set(df.columns)
        if not columnas_requeridas.issubset(columnas_archivo):
            faltantes = columnas_requeridas - columnas_archivo
            return {"error": f"Faltan columnas requeridas: {', '.join(faltantes)}"}

        if df.empty:
            return {"error": "El archivo está vacío o no contiene datos válidos."}

# Verificar si el DataFrame está vacío
    
    if df.empty:
        return {"error": "El archivo está vacío o no contiene datos válidos."}
  
    # 2. Eliminar duplicados exactos
    df.drop_duplicates(inplace=True)

#validadcion extra 
    esperadas = {
        "Nombre del lugar": "nombre",
        "Dirección Completa": "direccion",
        "Georeferencia": "georeferencia",
        "Fecha de registro": "fecha_registro"
    }

    df = df.rename(columns=esperadas)
    df = df.loc[:, ~df.columns.duplicated()]
    # Renombrar columnas esperadas
    df = df.rename(columns=esperadas)
    # Eliminar columnas duplicadas (¡clave para evitar el error!)
    df = df.loc[:, ~df.columns.duplicated()]    

# Agregar columnas faltantes con valor por defecto
    for col in esperadas.values():
        if col not in df.columns:
            if col == "fecha_registro":
                df[col] = pd.Timestamp.utcnow()
            else:
                df[col] = "Desconocido"
    # Eliminar columnas duplicadas de nuevo por seguridad
    df = df.loc[:, ~df.columns.duplicated()]

       
  
    


      #verifica caracteres raros
    df["nombre"] = df["nombre"].apply(normalizar_texto)
    df["direccion"] = df["direccion"].apply(normalizar_texto)


        # Validar y convertir la columna de fecha
    if "fecha_registro" in df.columns:
        df["fecha_registro"] = pd.to_datetime(df["fecha_registro"], errors="coerce")
        df = df.dropna(subset=["fecha_registro"])
    else:
        df["fecha_registro"] = pd.Timestamp.utcnow()  # o puedes usar None si prefieres

    # 4. Eliminar filas incompletas
    df = df.dropna(subset=["nombre", "direccion", "georeferencia"])

    # 5. Limpieza de espacios y formato
    df["nombre"] = df["nombre"].str.strip().str.title()
    df["direccion"] = df["direccion"].str.strip()
    df["georeferencia"] = df["georeferencia"].str.strip()

    # 6. Separar latitud y longitud
    df[["latitud", "longitud"]] = df["georeferencia"].str.split(",", expand=True).astype(float)

    # 7. Filtrar por rangos válidos de coordenadas
    df = df[
        df["latitud"].between(-90, 90) &
        df["longitud"].between(-180, 180)
    ]
    # Segmentar dirección completa
    df[["ciudad", "estado", "provincia", "pais"]] = df["direccion"].apply(segmentar_direccion)

    df.to_csv("datos_normalizados.csv", sep=";", index=False)
    insertar_datos(df, session)


    return RedirectResponse(url="/api/datos/" ,status_code=303)




@router.get("/descargar/", response_class=FileResponse)
async def descargar():
    return FileResponse("datos_normalizados.csv", media_type="text/csv", filename="lugares_normalizados.csv")




@router.get("/eliminar-bd/")
async def eliminar_bd():
    archivo_bd = "base.db"
    engine.dispose()  # Cierra todas las conexiones del engine global

    
    time.sleep(1.0)  # Espera breve para asegurar cierre en Windows

    if os.path.exists(archivo_bd):
        try:
            os.remove(archivo_bd)
            # Vuelve a crear las tablas después de eliminar la base de datos
            create_db_and_tables()
            return {"mensaje": "Base de datos eliminada y recreada correctamente."}
        except PermissionError:
            return {"error": "No se pudo eliminar la base de datos. Intenta de nuevo."}
    else:
        # Si no existe, igual crea las tablas por si acaso
        create_db_and_tables()
        return {"mensaje": "La base de datos no existía, pero las tablas han sido creadas."}