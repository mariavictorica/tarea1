from fastapi import FastAPI, Body, Path, Query, Request, HTTPException,Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel 
from models.computer import Computers as ComputerModel
from fastapi.encoders import jsonable_encoder

app = FastAPI()
app.title = "Mi primera aplicacion con FastAPI"
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="Credenciales Invalidas")

class User(BaseModel):
    email: str
    password: str

movies = [
    {
        "id": 1,
        "title": "Trainspotting",
        "overview": "Unos jóvenes de Edimburgo mantienen",
        "year": 1996,
        "rating": 10,
        "category": "Drama"
    },
    {
        "id": 2,
        "title": "Un lugar llamado Nottin Hill",
        "overview": "Ana Scott, tal tal tal",
        "year": 1999,
        "rating": 10,
        "category": "Romance"
    },
    {
        "id": 3,
        "title": "WALL-E",
        "overview": "Luego de pasar años limpiando la tierra",
        "year": 2008,
        "rating": 10,
        "category": "Animada"
    },
    {
        "id": 4,
        "title": "El Padrino",
        "overview": "Una adaptación ganadora",
        "year": 1972,
        "rating": 10,
        "category": "Crimen"
    },
    {
        "id": 5,
        "title": "Bob Esponja: La Pelicula",
        "overview": "Bob Esponja y Patricio viajan",
        "year": 2004,
        "rating": 10,
        "category": "Animada"
    },
    {
        "id": 6,
        "title": "Mujercitas",
        "overview": "En los primeros años que prosiguen a la guerra civil",
        "year": 2019,
        "rating": 8.5,
        "category": "Romance"
    },
    {
        "id": 7,
        "title": "Amadeus",
        "overview": "Antonio Salieri, composto d ela corte en Viena",
        "year": 1984,
        "rating": 9.6,
        "category": "Musica"
    },
    {
        "id": 8,
        "title": "El Ilusionista",
        "overview": "Viena, 1900. El ilusionista",
        "year": 2006,
        "rating": 8,
        "category": "Romance"
    },
    {
        "id": 9,
        "title": "El Origen",
        "overview": "Dom Cobb es un ladron con una extraña habilidad",
        "year": 2010,
        "rating": 9,
        "category": "Sci-Fi"
    },
    {
        "id": 10,
        "title": "Batman del futuro",
        "overview": "El joven protegido de uno de los superhéroes",
        "year": 2000,
        "rating": 10,
        "category": "Animada"
    },
]

class Movie(BaseModel):
    id: Optional[int] = None #Indicamos que es opcional
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=5, max_length=100)
    year: int = Field(le=2025)
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=5, max_length=15)

    class Config:
        json_schema_extra = {
            "example": {
                "id": len(movies) + 1,
                "title": "Mi Pelicula",
                "overview": "Descripción de la Película",
                "year": 2025,
                "rating": 6.6,
                "category": "Acción"
            }
        }

@app.get('/', tags=['Home'])
def message():
    return "Hello World"

@app.get('/movies', tags = ['Movies'], response_model = List[Movie], status_code = 200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).all()
    return JSONResponse(status_code = 200, content = jsonable_encoder(result))

@app.get('/movies/{id}', tags=['Movies'], response_model = Movie, status_code = 200)
def get_movies(id: int = Path(ge=1, le=2000)) -> Movie:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(status_code = 404, content = {"message": "No encontrado"})
    return JSONResponse(status_code = 200, content = jsonable_encoder(result))

@app.get('/movie/', tags=['Movies'], response_model = List[Movie])
def get_movie_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.category == category).all()
    if not result:
        return JSONResponse(status_code = 404, content = {"message": "No encontrado(s)"})
    return JSONResponse(content = jsonable_encoder(result))

@app.post('/movies', tags=['Movies'], response_model = dict, status_code = 201)
def create_movie(movie: Movie) -> dict:
    if(movies):
        db = Session()
        # Utilizamos el modelo y le pasamos la información que vamos a registrar
        new_movie = MovieModel(**movie.model_dump())
        # Ahora añadimos a la base de datos la pelicula
        db.add(new_movie)
        # Guardamos los datos
        db.commit()

        movies.append(movie)
        return JSONResponse(status_code = 201, content = {"message": "Se ha registrado la pelicula"})
    else:
        return JSONResponse(status_code = 400)

@app.delete('/movie/{id}', tags=['Movies'], response_model = dict, status_code = 200)
def delete_movie(id: int) -> dict:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(status_code = 404, content = {"message": "No encontrado"})
    db.delete(result)
    db.commit()
    return JSONResponse(status_code = 200, content = {"message": "Se ha eliminado la pelicula"})

@app.put('/movies/{id}', tags=['Movies'], response_model=dict, status_code=200)
def update_movie(id: int, movie: Movie) -> dict:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not result:
        return JSONResponse(status_code = 404, content = {"message": "No encontrado"})
    result.title = movie.title
    result.overview = movie.overview
    result.year = movie.year
    result.rating = movie.rating
    result.category = movie.category
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Se ha actualizado la pelicula"})
    
    

@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
        return JSONResponse(status_code = 200, content = token)
    



    
class Computer(BaseModel):
    id: Optional[int] = None
    brand: str = Field(min_length=2, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    color: str = Field(min_length=3, max_length=30)
    processor: str = Field(min_length=3, max_length=50)
    ram: int = Field(ge=1, le=128)
    storage: int = Field(ge=128, le=4096)
    price: float = Field(ge=100, le=10000)
    category: str = Field(min_length=3, max_length=20)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "brand": "Dell",
                "model": "XPS 15",
                "color": "Silver",
                "processor": "Intel Core i7",
                "ram": 16,
                "storage": 512,
                "price": 1499.99,
                "category": "Laptop"
            }
        }

computers = [
    {
        "id": 1, "brand": "Dell", "model": "XPS 15", "color": "Silver",
        "processor": "Intel Core i7-11800H", "ram": 16, "storage": 512,
        "price": 1499.99, "category": "Laptop"
    },
    {
        "id": 2, "brand": "Apple", "model": "MacBook Pro 14", "color": "Space Gray",
        "processor": "M1 Pro", "ram": 16, "storage": 1024,
        "price": 1999.99, "category": "Laptop"
    },
    {
        "id": 3, "brand": "HP", "model": "Omen 30L", "color": "Black",
        "processor": "AMD Ryzen 9 5900X", "ram": 32, "storage": 2048,
        "price": 2499.99, "category": "Desktop"
    },
    {
        "id": 4, "brand": "Lenovo", "model": "ThinkPad X1 Carbon", "color": "Black",
        "processor": "Intel Core i5-1135G7", "ram": 8, "storage": 256,
        "price": 1299.99, "category": "Laptop"
    },
    {
        "id": 5, "brand": "Asus", "model": "ROG Strix G15", "color": "Gray",
        "processor": "AMD Ryzen 7 5800H", "ram": 16, "storage": 1000,
        "price": 1399.99, "category": "Laptop"
    },
    {
        "id": 6, "brand": "MSI", "model": "Trident X", "color": "White",
        "processor": "Intel Core i9-10900K", "ram": 64, "storage": 2000,
        "price": 2999.99, "category": "Desktop"
    },
    {
        "id": 7, "brand": "Acer", "model": "Predator Helios 300", "color": "Black",
        "processor": "Intel Core i7-11800H", "ram": 16, "storage": 512,
        "price": 1299.99, "category": "Laptop"
    },
    {
        "id": 8, "brand": "Alienware", "model": "Aurora R13", "color": "Dark Gray",
        "processor": "Intel Core i9-12900KF", "ram": 32, "storage": 1000,
        "price": 2799.99, "category": "Desktop"
    },
    {
        "id": 9, "brand": "Microsoft", "model": "Surface Laptop 4", "color": "Platinum",
        "processor": "AMD Ryzen 7 4980U", "ram": 16, "storage": 512,
        "price": 1599.99, "category": "Laptop"
    },
    {
        "id": 10, "brand": "Custom Build", "model": "Gaming Pro", "color": "Black",
        "processor": "AMD Ryzen 9 5950X", "ram": 64, "storage": 4000,
        "price": 3499.99, "category": "Desktop"
    }
]

@app.get('/', tags=['home'])
def message():
    return HTMLResponse("<h1>Welcome to Computer Store API</h1>")


@app.get('/computers', tags=['Computers'], response_model=List[Computer], status_code=200, dependencies=[Depends(JWTBearer())])
def get_all_computers() -> List[Computer]:
    db = Session()
    result = db.query(ComputerModel).all()
    return JSONResponse(status_code = 200, content = jsonable_encoder(result))



@app.get('/computers/{id}', tags=['Computers'], response_model = Computer, status_code=200, dependencies=[Depends(JWTBearer())])
def get_computer(id: int = Path(ge=1, le=100)) -> Computer:
    db = Session()
    result = db.query(ComputerModel).filter(ComputerModel.id == id).first()
    if not result:
        return JSONResponse(status_code=404, content={"message": "Computadora no encontrada"})
    return JSONResponse(status_code=200,content = jsonable_encoder(result))


@app.post('/computers', tags=['Computers'], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_computer(computer: Computer) -> dict:
    db = Session()
    #Usar el modelo y pasarle infor a regitstrar
    new_computer = ComputerModel(**computer.model_dump())
    #Añair album desde la db
    db.add(new_computer)
    #Guardar los datos
    db.commit()
    computers.append(computer)
    return JSONResponse(status_code=201, content = {"message": "Computer creada correctamente"})

@app.put('/computers/{id}', tags=['Computers'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def update_computer(id:int, computer:Computer) -> dict:
    db = Session()
    result = db.query(ComputerModel).filter(ComputerModel.id == id).first()
    if not result:
        return JSONResponse(status_code=404, content={"message": "Computer not found"})
    result.brand = computer.brand
    result.model = computer.model
    result.color = computer.color
    result.ram = computer.ram
    result.storage = computer.storage
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Computer actualizada correctamente"})


@app.delete('/computers/{id}', tags=['Computers'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def delete_computer(id: int = Path(..., ge=1, le=100)) -> dict:
    db = Session()
    result = db.query(ComputerModel).filter(ComputerModel.id == id).first()
    if not result:
        return JSONResponse(status_code=404, content={"message": "Computer not found"})
    db.delete(result)
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Computer eliminada correctamente"})

@app.get('/computers/brand/', tags=['Computers'], response_model=List[dict], status_code=200, dependencies=[Depends(JWTBearer())])
def get_computer_by_brand(
    brand: str = Query(..., min_length=3, max_length=15, description="Nombre de la marca a buscar")
) -> List[dict]:
    db = Session()
    result = db.query(ComputerModel).filter(ComputerModel.brand == brand).all()
    if not result:
        return JSONResponse(status_code=404, content={"message": "No computers found for this genre"})
    return JSONResponse(status_code=200, content=jsonable_encoder(result))

#Endpoint para loggin, recibe crendeicales -> post
@app.post("/login", tags=['Auth'])
def loggin(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token: str = create_token(user.dict())
        return JSONResponse(status_code=200, content={"token":token})
    

