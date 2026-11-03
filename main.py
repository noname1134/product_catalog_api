from fastapi import FastAPI
from routers.products_router import router as products_router
from routers.users_router import router as users_router

app = FastAPI()
app.include_router(products_router)
app.include_router(users_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
