"""FastAPI route definitions for POST /v1/troubleshoot and GET /health (M6-01 & M6-02)."""

from fastapi import APIRouter, HTTPException, status
from fixgraph.contracts.public import Goal, HealthResponse, TroubleshootRequest
from fixgraph.service.troubleshoot import TroubleshootService

router = APIRouter()
_service_instance: TroubleshootService = None


def get_service() -> TroubleshootService:
    global _service_instance
    if _service_instance is None:
        _service_instance = TroubleshootService()
    return _service_instance


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check():
    """Health readiness check returning HTTP 200 with status ok."""
    try:
        service = get_service()
        if not service.catalog or len(service.catalog) == 0:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Deeplink catalog not initialized",
            )
        return HealthResponse(status="ok")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


@router.post("/v1/troubleshoot", response_model=Goal, status_code=status.HTTP_200_OK)
def troubleshoot_endpoint(request: TroubleshootRequest):
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

    try:
        service = get_service()
        goal, metrics = service.troubleshoot(request)
        return goal
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal troubleshooting error: {str(e)}",
        )
