from fastapi import FastAPI

from app.routers import items, claims

app = FastAPI(title="Lost & Found API")

app.include_router(items.router)
app.include_router(claims.router)