from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CREDENCIAIS PROTEGIDAS (Nunca expostas no front-end)
CAKTO_CLIENT_ID = "R50kJbZ68mXF3e6gpMdpzXrm4oSb0uRQazu0q9vi"
CAKTO_CLIENT_SECRET = "pqlU93417QYEsaZasiQ0Fjh8cotF9eSsHFfHR3hmEITefXu52jkmnnIOwVwKnjU2H1XT6V4niyKlrwhOvbPyiVyOh2Pd9QPS7TNUppfZhW1k3PPA26XpbOcP3t13lryU"
PRODUCT_LINK = "https://pay.cakto.com.br/SEU_ID_PRODUTO"

class CheckoutRequest(BaseModel):
    name: str
    email: str
    phone: str
    cpf: str
    zip_code: str
    street: str
    number: str

@app.post("/api/create-payment")
async def create_payment(data: CheckoutRequest):
    """
    Aqui o backend processaria a autenticação OAuth com a Cakto
    usando o CLIENT_ID e CLIENT_SECRET para gerar um token de checkout.
    """
    try:
        # Em um fluxo real, faríamos uma chamada POST à API da Cakto aqui.
        base_url = PRODUCT_LINK
        params = {
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "cpf": data.cpf,
            "zip_code": data.zip_code,
            "address": data.street,
            "number": data.number,
            "client_id": CAKTO_CLIENT_ID
        }
        
        # Simulando a resposta da API externa
        checkout_url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        
        return {"checkout_url": checkout_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
