from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.Lugares import Lugares


class Georeferencia(SQLModel, table=True):
    id_georeferencia: Optional[int] = Field(default=None, primary_key=True)
    latitud: float = Field(index=True)
    longitud: float = Field(index=True)

    id_lugar: Optional[int] = Field(default=None, foreign_key="lugares.id_lugar")
    lugar: Optional["Lugares"] = Relationship(back_populates="georeferencia")