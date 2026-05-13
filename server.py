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
PRODUCT_LINK = "https://pay.cakto.com.br/376mm6y_883600"

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
    Simula a geração de um link de checkout autenticado.
    Em um ambiente real, você faria um POST para a Cakto enviando o Client ID e Secret.
    """
    try:
        # Simulando a estrutura de URL da Cakto que aceita preenchimento automático
        # Certifique-se de substituir PRODUCT_LINK pelo link do seu produto real na Cakto
        base_url = PRODUCT_LINK 
        
        # Parâmetros que a Cakto geralmente utiliza para preenchimento via URL
        params = {
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "cpf": data.cpf,
            "zipcode": data.zip_code,
            "address": data.street,
            "number": data.number,
            "client_id": CAKTO_CLIENT_ID # ID da aplicação para rastreio
        }
        
        # Gerando a URL final codificada para evitar erros de leitura da API
        from urllib.parse import urlencode
        query_string = urlencode(params)
        checkout_url = f"{base_url}?{query_string}"
        
        return {"checkout_url": checkout_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")
