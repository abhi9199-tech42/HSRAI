"""HSRAI Production API Server.

Features:
- API key authentication
- Rate limiting per client
- Prometheus metrics
- Neo4j health checks
- Async request queuing with backpressure
- Structured logging
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from hsrai.logging_config import setup_logging
from hsrai.middleware import APIKeyAuth, MetricsCollector, RateLimiter
from hsrai.system.config import SystemConfig
from hsrai.system.controller import SystemController

logger = logging.getLogger(__name__)

_controller: Optional[SystemController] = None
_auth: Optional[APIKeyAuth] = None
_rate_limiter: Optional[RateLimiter] = None
_metrics: Optional[MetricsCollector] = None
_start_time: float = 0.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _controller, _auth, _rate_limiter, _metrics, _start_time
    setup_logging(
        level=os.environ.get("HSRAI_LOG_LEVEL", "INFO"),
        json_output=os.environ.get("HSRAI_ENV") == "production",
    )
    logger.info("Starting HSRAI API server")
    _start_time = time.time()
    _metrics = MetricsCollector()
    _rate_limiter = RateLimiter(
        max_requests=int(os.environ.get("HSRAI_RATE_LIMIT", "100")),
        window_seconds=60,
    )
    _auth = APIKeyAuth()
    api_key = os.environ.get("HSRAI_API_KEY")
    if api_key:
        _auth.add_key(api_key, "env")
    config = SystemConfig()
    _controller = SystemController(config=config)
    logger.info("HSRAI API server ready")
    yield
    logger.info("Shutting down HSRAI API server")
    if _controller:
        _controller.trust_manager.save_keys_if_configured()


app = FastAPI(
    title="HSRAI API",
    description="Hybrid Semantic Reasoning AI - Deterministic, Auditable, Cryptographically Verifiable Reasoning",
    version="1.0.0",
    lifespan=lifespan,
)


async def verify_api_key(request: Request) -> None:
    """Dependency: verify API key from X-API-Key header."""
    if _auth is None:
        return
    api_key = request.headers.get("X-API-Key")
    if not _auth(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide via X-API-Key header.",
        )


async def check_rate_limit(request: Request) -> None:
    """Dependency: enforce rate limiting per client IP."""
    if _rate_limiter is None:
        return
    client_ip = request.client.host if request.client else "unknown"
    allowed = await _rate_limiter.check(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
        )


# --- Request/Response Models ---

class ProcessRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Input text to process")
    request_id: Optional[str] = Field(None, max_length=128, description="Optional request ID")

class ProcessResponse(BaseModel):
    content: str
    format: str
    trust_certificate_id: Optional[str] = None
    metadata: dict = {}
    processing_time_ms: float = 0.0

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime_seconds: float
    certificates_issued: int
    neo4j_connected: bool
    requests_total: int
    errors_total: int

class MetricsResponse(BaseModel):
    requests_total: int
    errors_total: int
    avg_processing_time: float
    p99_processing_time: float
    certificates_issued: int

class VerifyRequest(BaseModel):
    certificate_id: str = Field(..., min_length=1)

class VerifyResponse(BaseModel):
    valid: bool
    message: str
    certificate_id: str

class ErrorResponse(BaseModel):
    error: str
    detail: str
    request_id: Optional[str] = None

class QueueStatusResponse(BaseModel):
    active_requests: int
    max_concurrent: int
    available_slots: int


# --- Endpoints ---

@app.post(
    "/process",
    response_model=ProcessResponse,
    responses={401: {"model": ErrorResponse}, 429: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    dependencies=[Depends(verify_api_key), Depends(check_rate_limit)],
)
async def process(req: ProcessRequest):
    start = time.monotonic()
    request_id = req.request_id or f"req_{hash(req.text) % 100000}"
    try:
        controller = _get_controller()
        output = await controller.process_request(req.text, request_id)
        elapsed = (time.monotonic() - start) * 1000
        trust_cert_id = None
        if output.trust_certificate:
            trust_cert_id = output.trust_certificate.certificate_id
        if _metrics:
            _metrics.record_request(elapsed / 1000.0, success=True)
            if trust_cert_id:
                _metrics.record_certificate()
        return ProcessResponse(
            content=output.content,
            format=output.format,
            trust_certificate_id=trust_cert_id,
            metadata=output.metadata,
            processing_time_ms=round(elapsed, 2),
        )
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        if _metrics:
            _metrics.record_request(elapsed / 1000.0, success=False)
        logger.error("Processing failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")


@app.get("/health", response_model=HealthResponse)
async def health():
    controller = _get_controller()
    neo4j_ok = False
    try:
        neo4j_ok = controller.knowledge.knowledge_sources[0]._connected if hasattr(controller.knowledge, 'knowledge_sources') else False
    except (AttributeError, IndexError):
        neo4j_ok = False

    return HealthResponse(
        status="ok",
        version="1.0.0",
        uptime_seconds=round(time.time() - _start_time, 1),
        certificates_issued=len(controller.trust_manager.certificate_chain),
        neo4j_connected=neo4j_ok,
        requests_total=_metrics.request_count if _metrics else 0,
        errors_total=_metrics.error_count if _metrics else 0,
    )


@app.get("/metrics")
async def metrics():
    if _metrics is None:
        return PlainTextResponse("Metrics not available\n", media_type="text/plain")
    return PlainTextResponse(_metrics.prometheus_text(), media_type="text/plain")


@app.get("/metrics/json", response_model=MetricsResponse)
async def metrics_json():
    if _metrics is None:
        return MetricsResponse(
            requests_total=0, errors_total=0, avg_processing_time=0.0,
            p99_processing_time=0.0, certificates_issued=0,
        )
    m = _metrics.get_metrics()
    return MetricsResponse(**m)


@app.post(
    "/verify",
    response_model=VerifyResponse,
    responses={401: {"model": ErrorResponse}},
    dependencies=[Depends(verify_api_key)],
)
async def verify(req: VerifyRequest):
    controller = _get_controller()
    cert = None
    for c in controller.trust_manager.certificate_chain:
        if c.certificate_id == req.certificate_id:
            cert = c
            break
    if cert is None:
        return VerifyResponse(
            valid=False,
            message=f"Certificate '{req.certificate_id}' not found",
            certificate_id=req.certificate_id,
        )
    valid = controller.trust_manager.verify_certificate(cert)
    return VerifyResponse(
        valid=valid,
        message="Certificate is valid" if valid else "Certificate verification failed",
        certificate_id=req.certificate_id,
    )


@app.get("/queue/status", response_model=QueueStatusResponse)
async def queue_status():
    controller = _get_controller()
    max_concurrent = controller.config.max_concurrent_requests
    active = controller.semaphore._value if hasattr(controller.semaphore, '_value') else 0
    return QueueStatusResponse(
        active_requests=max_concurrent - active,
        max_concurrent=max_concurrent,
        available_slots=active,
    )


def _get_controller() -> SystemController:
    global _controller
    if _controller is None:
        _controller = SystemController()
    return _controller
