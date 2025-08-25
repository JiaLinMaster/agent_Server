from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services import ChatService

bearer_scheme = HTTPBearer()
router = APIRouter(prefix="/chat", tags=["对话"])

class ChatRequest(BaseModel):
    question: str
    sessionId: str


class ChatResponse(BaseModel):
    answer: str
    sessionId: str
@router.post("",
             summary="用户对话接口",
             description="处理用户的对话请求，返回Agent的回答及会话ID，若未传入会话ID，则会生成一个会话ID",
             response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest,
                        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    接收用户输入的问题（question）以及可选的会话ID（session_id），并调用对话处理逻辑，返回回答结果及session_id。
    """
    api_key = credentials.credentials
    data = chat_request.model_dump()
    question = data.get("question")
    session_id = data.get("sessionId", ChatService.generate_session_id())

    result = await ChatService().process_chat(question, session_id, api_key)

    return JSONResponse({"answer": result, "sessionId": session_id})
