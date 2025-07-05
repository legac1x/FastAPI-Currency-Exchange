from fastapi import FastAPI
import uvicorn

from app.api.endpoints.users import users_router
from app.api.endpoints.currency import currency_router

app = FastAPI()

app.include_router(users_router)
app.include_router(currency_router)

if __name__ == "__main__":
    uvicorn.run(app, host='127.0.0.1', port=8000)