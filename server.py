from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CREDENCIAIS PROTEGIDAS
CAKTO_CLIENT_ID = "R50kJbZ68mXF3e6gpMdpzXrm4oSb0uRQazu0q9vi"
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
    Gera o link de checkout final utilizando o seu link direto da Cakto.
    """
    try:
        base_url = PRODUCT_LINK 
        
        # Parâmetros otimizados para o checkout da Cakto
        params = {
            "name": data.name,
            "email": data.email,
            "phone": data.phone,
            "document": data.cpf,         # CPF do cliente
            "zipcode": data.zip_code,      # CEP
            "address": data.street,       # Logradouro
            "address_number": data.number, # Número
            "client_id": CAKTO_CLIENT_ID
        }
        
        query_string = urlencode(params)
        checkout_url = f"{base_url}?{query_string}"
        
        print(f"URL de Checkout Gerada: {checkout_url}")
        
        return {"checkout_url": checkout_url}
        
    except Exception as e:
        print(f"Erro no processamento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
