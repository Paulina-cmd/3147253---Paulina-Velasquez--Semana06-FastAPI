from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
from database import engine, get_db

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Librería",
    description="API para gestión de autores y libros",
    version="1.0.0"
)

# AUTORES
@app.post("/autores/", response_model=schemas.Autor, status_code=status.HTTP_201_CREATED)
def crear_autor(autor: schemas.AutorCreate, db: Session = Depends(get_db)):
    db_autor = models.Autor(**autor.dict())
    db.add(db_autor)
    db.commit()
    db.refresh(db_autor)
    return db_autor

@app.get("/autores/", response_model=List[schemas.Autor])
def listar_autores(db: Session = Depends(get_db)):
    return db.query(models.Autor).all()

@app.get("/autores/{autor_id}", response_model=schemas.AutorConLibros)
def obtener_autor_con_libros(autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor

# LIBROS
@app.post("/libros/", response_model=schemas.LibroConAutor, status_code=status.HTTP_201_CREATED)
def crear_libro(libro: schemas.LibroCreate, db: Session = Depends(get_db)):
    # Verificar que el autor existe
    autor = db.query(models.Autor).filter(models.Autor.id == libro.autor_id).first()
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    
    db_libro = models.Libro(**libro.dict())
    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    return db_libro

@app.get("/libros/", response_model=List[schemas.LibroConAutor])
def listar_libros_con_autor(db: Session = Depends(get_db)):
    return db.query(models.Libro).all()

@app.get("/libros/buscar/")
def buscar_libros(
    titulo: str = Query(None, description="Buscar por título"),
    autor: str = Query(None, description="Buscar por autor"),
    precio_min: float = Query(None, description="Precio mínimo"),
    precio_max: float = Query(None, description="Precio máximo"),
    db: Session = Depends(get_db)
):
    if titulo:
        libros = crud.buscar_libros_por_titulo(db, titulo)
    elif autor:
        libros = crud.buscar_libros_por_autor(db, autor)
    elif precio_min is not None and precio_max is not None:
        libros = crud.obtener_libros_por_precio(db, precio_min, precio_max)
    else:
        libros = db.query(models.Libro).all()

    return {
        "libros": libros,
        "total": len(libros)
    }

@app.get("/estadisticas/")
def estadisticas_libros(db: Session = Depends(get_db)):
    """Estadísticas básicas de la librería"""
    total_libros = db.query(models.Libro).count()
    total_autores = db.query(models.Autor).count()

    if total_libros > 0:
        precios = [libro.precio for libro in db.query(models.Libro).all()]
        precio_promedio = sum(precios) / len(precios)
        precio_max = max(precios)
        precio_min = min(precios)
    else:
        precio_promedio = precio_max = precio_min = 0

    return {
        "total_libros": total_libros,
        "total_autores": total_autores,
        "precio_promedio": round(precio_promedio, 2),
        "precio_mas_alto": precio_max,
        "precio_mas_bajo": precio_min
    }

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de Librería"}