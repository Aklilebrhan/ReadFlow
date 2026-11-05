from typing import List, Dict, Any, Optional
import json
import httpx
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.shared.ai.base import (
    BaseChatProvider,
    BaseEmbeddingProvider,
    ChatCompletionResult,
    ChatCitation,
    TokenUsage
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """Google Gemini text-embedding-004 provider using Google Generative AI REST API."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_EMBEDDING_MODEL
        self._dim = 768

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            raise AIProviderError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:batchEmbedContents?key={self.api_key}"
        requests_payload = [
            {"model": f"models/{self.model}", "content": {"parts": [{"text": t}]}}
            for t in texts
        ]

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json={"requests": requests_payload})
                res.raise_for_status()
                data = res.json()
                return [item["values"] for item in data.get("embeddings", [])]
        except Exception as e:
            logger.error("Gemini batchEmbedContents failed: %s", str(e))
            raise AIProviderError(f"Gemini embedding error: {str(e)}")

    async def embed_query(self, query: str) -> List[float]:
        res = await self.embed_texts([query])
        return res[0]


class GeminiChatProvider(BaseChatProvider):
    """Google Gemini chat completions provider."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_CHAT_MODEL

    async def generate_rag_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None
    ) -> ChatCompletionResult:
        if not self.api_key:
            raise AIProviderError("GEMINI_API_KEY is not configured.")

        formatted_context = []
        citations_map = {}
        for idx, chunk in enumerate(context_chunks, start=1):
            doc_id = chunk.get("document_id", "")
            doc_title = chunk.get("document_title", "Document")
            page_num = chunk.get("page_number", 1)
            chunk_id = chunk.get("chunk_id", str(idx))
            text = chunk.get("text", "")
            citations_map[idx] = ChatCitation(
                citation_id=idx,
                document_id=doc_id,
                document_title=doc_title,
                page_number=page_num,
                chunk_id=chunk_id,
                snippet=text[:160] + "..." if len(text) > 160 else text,
                relevance_score=chunk.get("score")
            )
            formatted_context.append(f"[{idx}] (Doc: '{doc_title}', Page {page_num}):\n{text}")

        context_str = "\n\n".join(formatted_context)
        prompt = (
            f"You are ReadFlow, an expert AI document research assistant.\n"
            f"Ground your answer strictly in the provided Context passages.\n"
            f"Cite reference bracket numbers like [1], [2] when mentioning facts.\n"
            f"If information cannot be found, state: 'I could not find information in the provided document(s) to answer your question.'\n\n"
            f"Context Passages:\n{context_str}\n\n"
            f"Question:\n{query}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2}
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                text_ans = data["candidates"][0]["content"]["parts"][0]["text"]

                used_citations = []
                for cid, citation in citations_map.items():
                    if f"[{cid}]" in text_ans or not context_chunks:
                        used_citations.append(citation)

                if not used_citations and context_chunks:
                    used_citations = list(citations_map.values())[:3]

                return ChatCompletionResult(
                    answer=text_ans,
                    citations=used_citations,
                    token_usage=TokenUsage(prompt_tokens=200, completion_tokens=150, total_tokens=350, estimated_cost_usd=0.0001),
                    model=self.model,
                    provider="gemini"
                )
        except Exception as e:
            logger.error("Gemini generateContent failed: %s", str(e))
            raise AIProviderError(f"Gemini API error: {str(e)}")

    async def generate_summary(
        self,
        text_content: str,
        summary_type: str = "quick",
        instructions: Optional[str] = None
    ) -> str:
        prompt = f"Provide a {summary_type} summary of this document:\n\n{text_content[:8000]}"
        return await self._simple_completion(prompt)

    async def explain_passage(
        self,
        passage: str,
        explanation_type: str = "simple"
    ) -> str:
        prompt = f"Explain this passage with style '{explanation_type}':\n\n{passage}"
        return await self._simple_completion(prompt)

    async def generate_study_materials(
        self,
        text_content: str,
        material_type: str = "flashcards"
    ) -> Dict[str, Any]:
        prompt = f"Return {material_type} in JSON format matching {{'material_type': '{material_type}', 'items': [...]}}:\n\n{text_content[:6000]}"
        raw = await self._simple_completion(prompt)
        clean = raw.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean)
        except Exception:
            return {"material_type": material_type, "items": [{"raw_response": raw}]}

    async def _simple_completion(self, prompt: str) -> str:
        if not self.api_key:
            raise AIProviderError("GEMINI_API_KEY is not configured.")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
            res.raise_for_status()
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
