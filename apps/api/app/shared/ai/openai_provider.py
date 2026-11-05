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


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """Generates embeddings using OpenAI text-embedding-3 models."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.api_base = settings.OPENAI_API_BASE.rstrip("/")
        self._dim = 1536 if "small" in self.model else 3072

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            raise AIProviderError("OPENAI_API_KEY is not configured.")

        url = f"{self.api_base}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "input": texts,
            "model": self.model
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                return [item["embedding"] for item in data["data"]]
        except Exception as e:
            logger.error("OpenAI embedding generation failed: %s", str(e))
            raise AIProviderError(f"OpenAI embedding generation failed: {str(e)}")

    async def embed_query(self, query: str) -> List[float]:
        res = await self.embed_texts([query])
        return res[0]


class OpenAIChatProvider(BaseChatProvider):
    """Generates chat responses using OpenAI Chat Completions API."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_CHAT_MODEL
        self.api_base = settings.OPENAI_API_BASE.rstrip("/")

    async def generate_rag_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None
    ) -> ChatCompletionResult:
        if not self.api_key:
            raise AIProviderError("OPENAI_API_KEY is not configured.")

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

        system_prompt = system_instruction or (
            "You are ReadFlow, an expert AI document research assistant.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Ground your answer strictly in the provided Context passages.\n"
            "2. Whenever making a claim or citing a fact, cite the reference bracket number like [1], [2].\n"
            "3. If the answer cannot be found in the provided context, explicitly say: "
            "'I could not find information in the provided document(s) to answer your question.'\n"
            "4. Never invent page numbers or document facts not present in the context."
        )

        user_content = f"Context Passages:\n{context_str}\n\nUser Question:\n{query}"

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-4:])
        messages.append({"role": "user", "content": user_content})

        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                choice = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})

                # Extract used citation IDs from answer text (e.g. [1], [2])
                used_citations = []
                for cid, citation in citations_map.items():
                    if f"[{cid}]" in choice or not context_chunks:
                        used_citations.append(citation)

                # If no brackets found but chunks exist, include top citations
                if not used_citations and context_chunks:
                    used_citations = list(citations_map.values())[:3]

                return ChatCompletionResult(
                    answer=choice,
                    citations=used_citations,
                    token_usage=TokenUsage(
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        total_tokens=usage.get("total_tokens", 0),
                        estimated_cost_usd=(usage.get("total_tokens", 0) / 1000) * 0.0003
                    ),
                    model=self.model,
                    provider="openai"
                )
        except Exception as e:
            logger.error("OpenAI chat generation failed: %s", str(e))
            raise AIProviderError(f"OpenAI chat generation error: {str(e)}")

    async def generate_summary(
        self,
        text_content: str,
        summary_type: str = "quick",
        instructions: Optional[str] = None
    ) -> str:
        prompt = f"Provide a {summary_type} summary of the following document content:\n\n{text_content[:8000]}"
        return await self._simple_completion(prompt)

    async def explain_passage(
        self,
        passage: str,
        explanation_type: str = "simple"
    ) -> str:
        prompt = f"Explain the following passage with style '{explanation_type}':\n\n{passage}"
        return await self._simple_completion(prompt)

    async def generate_study_materials(
        self,
        text_content: str,
        material_type: str = "flashcards"
    ) -> Dict[str, Any]:
        prompt = (
            f"Generate {material_type} from the following text in JSON format matching "
            f"{{'material_type': '{material_type}', 'items': [...]}}:\n\n{text_content[:6000]}"
        )
        response_text = await self._simple_completion(prompt)
        try:
            # Clean markdown code block if present
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception:
            return {"material_type": material_type, "items": [{"raw_response": response_text}]}

    async def _simple_completion(self, prompt: str) -> str:
        if not self.api_key:
            raise AIProviderError("OPENAI_API_KEY is not configured.")

        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(url, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"]
