from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.abspath(os.path.join(BASE_DIR, "../output"))
CHAT_DB_PATH = os.path.join(DB_DIR, "chat_history.db")

engine = create_engine(f"sqlite:///{CHAT_DB_PATH}", echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
chat_session = SessionLocal()

# 테이블 생성
def init_chat_db():
    Base.metadata.create_all(bind=engine)

# 채팅방 테이블
class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255))
    kpi_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    messages = relationship("ChatMessage", back_populates="chatroom")

# 채팅 메시지 테이블
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    chatroom_id = Column(Integer, ForeignKey("chat_rooms.id"))
    sender = Column(String(10))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)

    chatroom = relationship("ChatRoom", back_populates="messages")

