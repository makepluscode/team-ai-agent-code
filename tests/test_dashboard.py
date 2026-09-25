import pytest
from fastapi.testclient import TestClient
from src.app.main import app
from src.mcp.redact import redact_text, is_sensitive_query
from src.mcp.db import init_db, query_customer_contracts

client = TestClient(app)

def test_dashboard_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "팀 AI 에이전트 대시보드" in response.text
    assert "로컬 LLM" in response.text
    assert "상용 API" in response.text

def test_chat_general_query():
    response = client.post("/api/chat", data={"message": "안녕하세요 반갑습니다"})
    assert response.status_code == 200
    assert "상용 API" in response.text
    assert "안녕하세요" in response.text

def test_chat_sensitive_db_query():
    response = client.post("/api/chat", data={"message": "에이아이솔루션 고객 계약 조회해줘"})
    assert response.status_code == 200
    assert "로컬 LLM" in response.text
    # 전화번호와 금액이 보안 마스킹되었는지 검증
    assert "[연락처-보안마스킹]" in response.text or "[금액-대외비]" in response.text
    assert "010-1234-5678" not in response.text

def test_meeting_mock_upload():
    response = client.post("/api/meeting/mock-upload")
    assert response.status_code == 200
    assert "주간 스프린트 & 아키텍처 점검" in response.text
    assert "로컬 Whisper 전사" in response.text

def test_redact_unit():
    raw = "고객 전화번호는 010-1234-5678 이고 계약금액은 50000000원 입니다. 메일은 test@example.com 입니다."
    redacted, was_redacted = redact_text(raw)
    assert was_redacted is True
    assert "010-1234-5678" not in redacted
    assert "test@example.com" not in redacted
    assert "[연락처-보안마스킹]" in redacted
    assert "[이메일-보안마스킹]" in redacted
    assert "[금액-대외비]" in redacted

def test_sensitive_query_detection():
    assert is_sensitive_query("고객사 정보 보여줘") is True
    assert is_sensitive_query("계약 금액이 얼마야?") is True
    assert is_sensitive_query("오늘 날씨 어때?") is False
