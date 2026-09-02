from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation_service import conversation_service
from app.logging_config import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
def handle_chat(request: ChatRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")
    try:
        result = conversation_service.process_chat(
            conversation_id=request.conversation_id,
            user_text=text,
            generate_audio=request.generate_audio
        )
        return result
    except Exception as e:
        logger.error("Chat processing error: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")

@router.post("/stream")
def stream_chat_endpoint(request: ChatRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text prompt cannot be empty.")
    try:
        generator = conversation_service.stream_chat(
            conversation_id=request.conversation_id,
            user_text=text
        )
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        logger.error("Streaming chat error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to initialize streaming response.")
