from fastapi import APIRouter, Depends, HTTPException
from langchain_core.exceptions import ModelError, ModelRateLimitError
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ChatRequest, ChatResponse
from app.services.chat import answer_question
from app.services.sql_validator import UnsafeSQLError

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        return answer_question(db, request.question)
    except UnsafeSQLError as e:
        raise HTTPException(status_code=400, detail=f"Query blocked for safety: {e}")
    except DBAPIError:
        raise HTTPException(status_code=400, detail="Could not run the generated query. Try rephrasing.")
    except ModelRateLimitError:
        raise HTTPException(status_code=429, detail="AI rate limit reached. Please wait a minute and retry.")
    except ModelError:
        raise HTTPException(status_code=503, detail="AI service is unavailable. Please try again later.")
