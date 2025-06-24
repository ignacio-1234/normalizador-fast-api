from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.Lugares import Lugares

class Direcciones(SQLModel, table=True):
    id_direccion: Optional[int] = Field(default=None, primary_key=True)
    direccion: str = Field(index=True)
    ciudad: str = Field(index=True)
    estado: str = Field(index=True)
    provincia: str = Field(index=True)
    pais: str = Field(index=True)

    id_lugar: Optional[int] = Field(default=None, foreign_key="lugares.id_lugar")
    lugar: Optional["Lugares"] = Relationship(back_populates="direccion")