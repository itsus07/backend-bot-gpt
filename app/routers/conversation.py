from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app import database, models, schemas, llm_service
import shutil
import os

router = APIRouter()

@router.post("/conversation", response_model=schemas.ConversationResponse)
def create_conversation(request: schemas.CreateConversationRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.user_id == 1).first()
    if not user:
        user = models.User(email="demo@botgpt.com", phone="1234567890")
        db.add(user)
        db.commit()

    db_conv = models.Conversation(user_id=1, title=request.message[:30], type=request.type)
    db.add(db_conv)
    db.commit()
    db.refresh(db_conv)

    user_msg = models.Message(
        conversation_id=db_conv.conversation_id,
        sent_by="user",
        text=request.message,
        sequence=1
    )
    db.add(user_msg)
    reply_text = llm_service.get_llm_response([], request.message)

    ai_msg = models.Message(
        conversation_id=db_conv.conversation_id,
        sent_by="assistant",
        text=reply_text,
        sequence=2
    )
    db.add(ai_msg)
    db.commit()

    return {"conversation_id": str(db_conv.conversation_id), "reply": reply_text}

@router.post("/conversation/{id}/messages", response_model=schemas.MessageResponse)
def send_message(id: str, request: schemas.MessageRequest, db: Session = Depends(database.get_db)):
    conv_id = int(id)

    conv = db.query(models.Conversation).filter(models.Conversation.conversation_id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    history = db.query(models.Message).filter(models.Message.conversation_id == conv_id).order_by(models.Message.sequence).all()
    next_seq = history[-1].sequence + 1 if history else 1

    context_text = ""
    if conv.type == "rag":
        docs = db.query(models.Document).filter(models.Document.conversation_id == conv_id).all()
        for doc in docs:
            try:
                with open(doc.path, "r") as f:
                    context_text += f.read() + "\n"
            except:
                pass

    user_msg = models.Message(conversation_id=conv_id, sent_by="user", text=request.message, sequence=next_seq)
    db.add(user_msg)
    db.commit()

    reply_text = llm_service.get_llm_response(history, request.message, context_text)

    ai_msg = models.Message(conversation_id=conv_id, sent_by="assistant", text=reply_text, sequence=next_seq + 1)
    db.add(ai_msg)
    db.commit()

    return {"reply": reply_text}

@router.get("/conversation", response_model=list[schemas.ConversationDetail])
def list_conversations(db: Session = Depends(database.get_db)):
    convs = db.query(models.Conversation).all()
    return [{"conversation_id": str(c.conversation_id), "title": c.title, "update_date": c.update_date} for c in convs]

@router.delete("/conversation/{id}")
def delete_conversation(id: str, db: Session = Depends(database.get_db)):
    conv = db.query(models.Conversation).filter(models.Conversation.conversation_id == int(id)).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"status": "deleted"}

@router.post("/conversation/{id}/upload")
def upload_document(id: str, file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    conv_id = int(id)
    file_location = f"data/uploads/{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = models.Document(conversation_id=conv_id, filename=file.filename, path=file_location)
    db.add(doc)

    conv = db.query(models.Conversation).filter(models.Conversation.conversation_id == conv_id).first()
    conv.type = "rag"
    
    db.commit()
    return {"status": "uploaded", "filename": file.filename}