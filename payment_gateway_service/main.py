from fastapi import FastAPI
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment-gateway")

app = FastAPI(title="Mock Payment Gateway Service")


class RefundRequest(BaseModel):
	return_id: str
	amount: int
	currency: str


@app.post("/refund")
async def refund(req: RefundRequest) -> dict:
	logger.info("Processing mock refund: return_id=%s amount=%s currency=%s", req.return_id, req.amount, req.currency)
	return {"status": "success", "return_id": req.return_id}
