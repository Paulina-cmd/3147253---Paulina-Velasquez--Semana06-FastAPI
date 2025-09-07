import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

# Crear tablas de prueba
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_crear_autor():
    response = client.post(
        "/autores/",
        json={"nombre": "Gabriel García Márquez", "nacionalidad": "Colombiana"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Gabriel García Márquez"
    assert data["nacionalidad"] == "Colombiana"

def test_crear_libro_con_autor():
    # Crear autor primero
    autor_response = client.post(
        "/autores/",
        json={"nombre": "Isabel Allende", "nacionalidad": "Chilena"}
    )
    autor_id = autor_response.json()["id"]

    # Crear libro
    response = client.post(
        "/libros/",
        json={
            "titulo": "La Casa de los Espíritus",
            "precio": 25.99,
            "paginas": 450,
            "autor_id": autor_id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == "La Casa de los Espíritus"
    assert data["precio"] == 25.99
    assert data["autor"]["nombre"] == "Isabel Allende"

def test_validacion_precio_negativo():
    response = client.post(
        "/libros/",
        json={
            "titulo": "Libro Inválido",
            "precio": -10.99,
            "paginas": 100,
            "autor_id": 1
        }
    )
    assert response.status_code == 422  # Error de validación

def test_listar_autores():
    response = client.get("/autores/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # Debería tener al menos los 2 autores que creamos

def test_obtener_autor_con_libros():
    # Primero obtener el ID de un autor existente
    autores_response = client.get("/autores/")
    autor_id = autores_response.json()[0]["id"]
    
    response = client.get(f"/autores/{autor_id}")
    assert response.status_code == 200
    data = response.json()
    assert "libros" in data

def test_buscar_libros_por_titulo():
    response = client.get("/libros/buscar/?titulo=Espíritus")
    assert response.status_code == 200
    data = response.json()
    assert "libros" in data
    assert "total" in data

def test_estadisticas():
    response = client.get("/estadisticas/")
    assert response.status_code == 200
    data = response.json()
    assert "total_libros" in data
    assert "total_autores" in data
    assert "precio_promedio" in data