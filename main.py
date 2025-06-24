from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routes.transform import router as transform
from database import create_db_and_tables

app= FastAPI()
create_db_and_tables()

# Mount static files directory for serving static content like CSS, JS, images, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Root endpoint to serve the main HTML page
@app.get("/",response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})

# Include the transform router(y por si queiro agregar mas rutas)
app.include_router(transform, prefix="/api", tags=["transform"])
