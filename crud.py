from sqlalchemy.orm import Session
from sqlalchemy import or_
import models

def buscar_libros_por_titulo(db: Session, busqueda: str):
    """Buscar libros por título"""
    return db.query(models.Libro).filter(
        models.Libro.titulo.contains(busqueda)
    ).all()

def buscar_libros_por_autor(db: Session, nombre_autor: str):
    """Buscar libros por nombre del autor"""
    return db.query(models.Libro).join(models.Autor).filter(
        models.Autor.nombre.contains(nombre_autor)
    ).all()

def obtener_libros_por_precio(db: Session, precio_min: float, precio_max: float):
    """Obtener libros en rango de precio"""
    return db.query(models.Libro).filter(
        models.Libro.precio >= precio_min,
        models.Libro.precio <= precio_max
    ).all()