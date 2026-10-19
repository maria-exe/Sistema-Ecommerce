from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pagamento_service import Pagamento
import uvicorn

service = Pagamento()

app = FastAPI()

class ResultadoPagamento(BaseModel):
    id_pedido: str
    status: str

@app.post("/pagamento")
async def pagamento(dados: ResultadoPagamento):
    try:
        if dados.status == "aprovado":
            service.publicar_evento(dados.model_dump(),"pagamento.aprovado")
        else:
            service.publicar_evento(dados.model_dump(),"pagamento.recusado")
    
    except Exception as exc:
        raise HTTPException(status_code=500)

    return {
        "mensagem": "Webhook recebido"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)