from fastapi import FastAPI
import uvicorn
from app.api.endpoints.users import user_router
from app.api.endpoints.currency import currency_router

app = FastAPI()

app.include_router(user_router)
app.include_router(currency_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)