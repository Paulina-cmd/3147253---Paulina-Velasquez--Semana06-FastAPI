# Usando SQLAlchemy ORM
from sqlalchemy.orm import Session
from models import Autor

def obtener_todos_autores(db: Session):
    return db.query(Autor).all()

autores = obtener_todos_autores()
for autor in autores:
    print(f"ID: {autor.id}, Nombre: {autor.nombre}, Nacionalidad: {autor.nacionalidad}")

