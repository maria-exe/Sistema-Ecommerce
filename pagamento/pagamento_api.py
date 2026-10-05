from fastapi import FastAPI

app = FastAPI()

@app.post("/pagamento")
async def pagamento():
    return