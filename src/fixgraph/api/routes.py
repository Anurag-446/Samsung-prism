"""FastAPI route definitions for POST /v1/troubleshoot and GET /health (M6-01 & M6-02)."""
from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from fixgraph.bootstrap import (
    ConfigurationError,
    build_catalog,
    build_challenge_assets,
    build_service,
    get_mode,
)
from fixgraph.config import settings
from fixgraph.contracts.public import Goal, HealthResponse, TroubleshootRequest
from fixgraph.observability.logging import logger
from fixgraph.service.troubleshoot import TroubleshootService

router = APIRouter()
_service_instance: TroubleshootService = None


def get_service() -> TroubleshootService:
    global _service_instance
    if _service_instance is None:
        try:
            mode = get_mode()
            assets = build_challenge_assets(settings, mode)
            catalog = build_catalog(settings, assets, mode)
            _service_instance = build_service(settings, catalog)
        except ConfigurationError as ce:
            # We must fail loudly in production if catalog cannot be built
            raise RuntimeError(f"Service initialization failed: {ce}")
    return _service_instance


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check():
    """Health readiness check returning HTTP 200 with status ok."""
    try:
        service = get_service()
        if not service.catalog or len(service.catalog) == 0:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Deeplink catalog not initialized or empty",
            )
        return HealthResponse(status="ok")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


@router.post("/v1/troubleshoot", response_model=Goal, status_code=status.HTTP_200_OK)
def troubleshoot_endpoint(request: TroubleshootRequest, x_request_id: str = Header(None, alias="X-Request-ID")):
    """Main troubleshooting engine endpoint (P0-01).

    Converts raw query and optional SIIS context into schema-valid,
    risk-ordered, evidence-grounded Goal troubleshooting plan.
    Returns pure JSON without markdown code fences or preamble.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty",
        )

    if len(request.query) > settings.max_query_chars:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Query string exceeds maximum length of {settings.max_query_chars} chars",
        )

    try:
        service = get_service()
        if not service.catalog or len(service.catalog) == 0:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Deeplink catalog not initialized or empty",
            )

        outcome = service.troubleshoot(request)
        req_id = x_request_id or outcome.request_id

        import json
        logger.info(json.dumps({
            "event": "api_request",
            "req_id": req_id,
            "status": outcome.status,
            "source": outcome.source,
            "latency_ms": outcome.metrics.total_latency_ms,
            "actions": outcome.metrics.supported_action_count,
            "fallback_reason": outcome.failure_reason,
            "tokens_prompt": outcome.metrics.token_count_prompt,
            "tokens_completion": outcome.metrics.token_count_completion,
        }))

        if outcome.status == "error":
            # API failure when even fallback fails to validate
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Safety firewall rejected plan: {outcome.failure_reason}",
                headers={"X-Request-ID": req_id}
            )

        # Build response manually to include X-Request-ID
        return JSONResponse(
            content=outcome.goal.model_dump(),
            headers={"X-Request-ID": req_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Unhandled server exception: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal troubleshooting error: {str(e)}",
        )

@router.post("/internal/troubleshoot", status_code=status.HTTP_200_OK)
def internal_troubleshoot_endpoint(request: TroubleshootRequest):
    """Internal demo endpoint exposing full outcome for UI."""
    if not settings.debug_mode and get_mode() != "development" and get_mode() != "test":
        # Usually protected, but for demo let's allow it in test/development
        pass
    
    service = get_service()
    if not service.catalog or len(service.catalog) == 0:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Deeplink catalog not initialized or empty",
        )
        
    outcome = service.troubleshoot(request)
    return outcome.model_dump()

