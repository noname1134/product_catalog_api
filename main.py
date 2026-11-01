from fastapi import FastAPI
from routers.products_router import router

app = FastAPI()
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
