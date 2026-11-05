from app.shared.ai.factory import get_chat_provider
from app.modules.explanation.schemas import ExplainRequest, ExplainResponse


class ExplanationService:
    """Service providing contextual explanations for highlighted text passages."""

    def __init__(self):
        self.ai = get_chat_provider()

    async def explain(self, req: ExplainRequest) -> ExplainResponse:
        result = await self.ai.explain_passage(
            passage=req.passage,
            explanation_type=req.explanation_type.value
        )
        return ExplainResponse(
            explanation=result,
            explanation_type=req.explanation_type.value,
            passage_preview=req.passage[:150] + "..." if len(req.passage) > 150 else req.passage
        )


explanation_service = ExplanationService()
