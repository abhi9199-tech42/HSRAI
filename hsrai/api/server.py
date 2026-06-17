from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncio
import logging

from hsrai.system.controller import SystemController
from hsrai.system.config import SystemConfig

logger = logging.getLogger(__name__)

app = FastAPI(
    title="HSRAI API",
    description="Hybrid Semantic Reasoning AI - Deterministic, Auditable, Cryptographically Verifiable Reasoning",
    version="1.0.0",
)

_controller: Optional[SystemController] = None


def _get_controller() -> SystemController:
    global _controller
    if _controller is None:
        _controller = SystemController()
    return _controller


class ProcessRequest(BaseModel):
    text: str
    request_id: Optional[str] = None


class ProcessResponse(BaseModel):
    content: str
    format: str
    trust_certificate_id: Optional[str] = None
    metadata: dict = {}


class HealthResponse(BaseModel):
    status: str
    version: str
    test_count: int


class VerifyRequest(BaseModel):
    content: str
    certificate_id: str
    signature: str


class VerifyResponse(BaseModel):
    valid: bool
    message: str


@app.post("/process", response_model=ProcessResponse)
async def process(req: ProcessRequest):
    try:
        controller = _get_controller()
        output = await controller.process_request(req.text, req.request_id)
        return ProcessResponse(
            content=output.content,
            format=output.format,
            trust_certificate_id=output.metadata.get("trust_certificate_id"),
            metadata=output.metadata,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")


@app.get("/health", response_model=HealthResponse)
async def health():
    controller = _get_controller()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        test_count=len(controller.trust_manager.certificate_chain),
    )


@app.post("/verify", response_model=VerifyResponse)
async def verify(req: VerifyRequest):
    try:
        controller = _get_controller()
        from hsrai.core.models import TrustCertificate

        cert = TrustCertificate(
            certificate_id=req.certificate_id,
            issuer_id="HSRAI_API",
            subject_id=req.content,
            trust_score=1.0,
            timestamp=0.0,
            signature=req.signature,
            claims={},
        )
        valid = controller.trust_manager.verify_certificate(cert)
        if valid:
            return VerifyResponse(valid=True, message="Certificate is valid")
        else:
            return VerifyResponse(valid=False, message="Certificate verification failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {e}")


@app.get("/graph/{request_id}")
async def get_graph(request_id: str):
    return {
        "request_id": request_id,
        "nodes": [],
        "edges": [],
        "message": "Graph retrieval not yet implemented",
    }


@app.post("/plugins")
async def register_plugin():
    return {"status": "success", "message": "Plugin registration not yet implemented"}
