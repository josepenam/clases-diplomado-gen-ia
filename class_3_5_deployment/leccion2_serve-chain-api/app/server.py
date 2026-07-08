"""FastAPI service that exposes a simple LangChain (LCEL) summarization chain as an API.

We wrap the chain (`prompt | llm`) in a plain FastAPI app — a durable, transferable skill
for putting any model behind an HTTP endpoint. The interactive "playground" is FastAPI's
built-in Swagger UI at /docs.
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()  # reads OPENAI_API_KEY (and any other vars) from a local .env file

logger = logging.getLogger("summarization")

# --- The LangChain chain ------------------------------------------------------
summarization_assistant_template = """\
You are a text summarization bot. Your expertise is exclusively in analyzing and
summarizing user-provided texts. Create a concise and comprehensive summary of the
provided text, retaining all crucial information in a shorter form.

Text for summarization:
{text_for_summarization}"""

summarization_prompt = PromptTemplate(
    input_variables=["text_for_summarization"],
    template=summarization_assistant_template,
)

llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
summarization_chain = summarization_prompt | llm


# --- Request / response models ------------------------------------------------
class SummarizeRequest(BaseModel):
    text: str = Field(..., description="The text to summarize.")


class SummarizeResponse(BaseModel):
    summary: str


# --- FastAPI app --------------------------------------------------------------
app = FastAPI(
    title="LangChain Summarization API",
    version="2.0",
    description=(
        "Serves a simple LangChain (LCEL) summarization chain via FastAPI. "
        "Try it interactively at /docs."
    ),
)


@app.get("/")
def health():
    """Liveness check — handy for fly.io and load balancers."""
    return {"status": "ok", "service": "summarization", "docs": "/docs"}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """Summarize a block of text.

    The text travels in the request body (unlike a query string, which is
    length-limited), so this handles long documents.
    """
    try:
        result = await summarization_chain.ainvoke(
            {"text_for_summarization": request.text}
        )
    except Exception:
        # Log the real error server-side; return a generic message to the client.
        logger.exception("Summarization failed")
        raise HTTPException(status_code=502, detail="Summarization failed; check server logs.")
    return SummarizeResponse(summary=result.content)


@app.post("/summarize/stream")
async def summarize_stream(request: SummarizeRequest):
    """Stream the summary token-by-token as Server-Sent Events (SSE)."""

    async def event_generator():
        try:
            async for chunk in summarization_chain.astream(
                {"text_for_summarization": request.text}
            ):
                if chunk.content:
                    yield f"data: {chunk.content}\n\n"
        except Exception:
            logger.exception("Streaming summarization failed")
            yield "event: error\ndata: Summarization failed; check server logs.\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    # 0.0.0.0 so the app is reachable from outside the container; PORT is set by
    # the platform (fly.io) and defaults to 8000 for local runs.
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
