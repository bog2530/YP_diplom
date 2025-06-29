from api.v1.genres import router as genres_router
from api.v1.films import router as films_router
from api.v1.persons import router as persons_router


routers = [
    genres_router,
    films_router,
    persons_router,
]
