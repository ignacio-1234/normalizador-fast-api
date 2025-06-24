from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


from models.Direcciones import Direcciones
from models.Georeferencia import Georeferencia

class Lugares(SQLModel, table=True):
    id_lugar: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)

    direccion: Optional["Direcciones"] = Relationship(back_populates="lugar")
    georeferencia: Optional["Georeferencia"] = Relationship(back_populates="lugar")
    fecha_registro: Optional[datetime] = Field(default_factory=datetime.now)