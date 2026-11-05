from fastapi import APIRouter
from app.modules.explanation.schemas import ExplainRequest, ExplainResponse
from app.modules.explanation.service import explanation_service

router = APIRouter(prefix="/explain", tags=["Document Explanation"])


@router.post("", response_model=ExplainResponse)
async def explain_selected_passage(request: ExplainRequest):
    """Explains a selected passage simply, technically, or extracts key definitions."""
    return await explanation_service.explain(request)
