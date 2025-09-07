from pydantic import BaseModel, validator
from typing import List, Optional

class AutorBase(BaseModel):
    nombre: str
    nacionalidad: str

class AutorCreate(AutorBase):
    pass

class Autor(AutorBase):
    id: int

    class Config:
        from_attributes = True

class LibroBase(BaseModel):
    titulo: str
    precio: float
    paginas: int
    autor_id: Optional[int] = None

    @validator('precio')
    def validar_precio(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v

    @validator('paginas')
    def validar_paginas(cls, v):
        if v <= 0:
            raise ValueError('El número de páginas debe ser mayor a 0')
        return v

    @validator('titulo')
    def validar_titulo(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('El título no puede estar vacío')
        return v.strip()

class LibroCreate(LibroBase):
    pass

class LibroConAutor(LibroBase):
    id: int
    autor: Optional[Autor] = None

    class Config:
        from_attributes = True

class AutorConLibros(Autor):
    libros: List[LibroBase] = []

    class Config:
        from_attributes = True