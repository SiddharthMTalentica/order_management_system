import uuid
from typing import Callable
from fastapi import Request


async def request_id_middleware(request: Request, call_next: Callable):
	request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
	request.state.request_id = request_id
	response = await call_next(request)
	response.headers["X-Request-ID"] = request_id
	return response
