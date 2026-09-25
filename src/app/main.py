import html
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.mcp.db import init_db, query_customer_contracts
from src.mcp.redact import redact_text, is_sensitive_query

app = FastAPI(title="Team AI Agent Dashboard")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# DB 초기화
init_db()

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "system_status": "온라인",
            "local_model": "qwen3.5:9b (GPU)",
            "cloud_model": "deepseek-flash (API)",
            "pending_inquiries": 3,
            "today_meetings": 2,
            "wiki_count": 28,
            "protection_rate": "100%",
        }
    )

@app.post("/api/chat", response_class=HTMLResponse)
async def chat_endpoint(request: Request, message: str = Form(...)):
    user_msg_safe = html.escape(message.strip())
    now_str = datetime.now().strftime("%H:%M:%S")
    msg_id = str(uuid.uuid4())[:8]

    # 민감 정보 및 사내 DB 관련 질의인지 판별
    if is_sensitive_query(user_msg_safe):
        # 3등급 데이터 -> 로컬 처리 경로
        route = "local"
        route_badge = "🔒 로컬 LLM (사내 DB·가명화)"
        badge_class = "route local"
        
        # 사내 DB 검색 수행
        db_results = query_customer_contracts("에이아이솔루션" if "고객" in user_msg_safe or "계약" in user_msg_safe else "솔루션")
        if db_results:
            row = db_results[0]
            raw_summary = (
                f"사내 DB 조회 결과:\n"
                f"- 고객사: {row['company']} ({row['name']})\n"
                f"- 연락처: {row['phone']} / 이메일: {row['email']}\n"
                f"- 계약명: {row['contract_title']}\n"
                f"- 계약액: {row['amount']:,}원 ({row['status']})\n"
                f"※ 보안 정책: 연락처와 계약 금액은 외부 클라우드로 전송하지 않고 로컬에서 안전하게 가명화했습니다."
            )
            # 가명화 적용
            redacted_summary, was_redacted = redact_text(raw_summary)
            bot_reply = redacted_summary
        else:
            bot_reply = "사내 DB에서 일치하는 고객 및 계약 기록을 찾을 수 없습니다 (로컬 검증 완료)."
            
    else:
        # 1등급/2등급 데이터 -> 상용 API 경로
        route = "api"
        route_badge = "☁️ 상용 API (지식·요약)"
        badge_class = "route api"
        
        if "안녕" in user_msg_safe:
            bot_reply = "안녕하세요! 소규모 팀을 위한 헤르메스 팀 에이전트 대시보드입니다. 사내 지식 검색, 미팅 회의록 정리, 업무 예약 처리를 도와드립니다."
        elif "위키" in user_msg_safe:
            bot_reply = "사내 위키(`wiki/`)에서 관련 문서를 검색했습니다:\n- [wiki/faq.md#L12-L30] 원격 근무 및 배포 가이드라인\n- [wiki/roles.md#L5] 5인 팀 업무 역할 분담 매뉴얼"
        else:
            bot_reply = f"질의하신 '{user_msg_safe}'에 대한 답변입니다. 일반 업무 질의는 상용 클라우드 API를 통해 빠르고 정확하게 분석되어 전달되었습니다."

    # HTMX 스왑용 HTML 조각 반환
    response_html = f"""
    <div class="chat-item user" id="msg-{msg_id}-user">
      <div class="bubble user-bubble">
        <div class="bubble-meta">나 · {now_str}</div>
        <div class="bubble-text">{user_msg_safe}</div>
      </div>
    </div>
    <div class="chat-item bot" id="msg-{msg_id}-bot">
      <div class="bubble bot-bubble">
        <div class="bubble-meta">
          <span class="{badge_class}">{route_badge}</span> · {now_str}
        </div>
        <div class="bubble-text" style="white-space: pre-wrap;">{html.escape(bot_reply)}</div>
      </div>
    </div>
    """
    return HTMLResponse(content=response_html)

@app.post("/api/meeting/mock-upload", response_class=HTMLResponse)
async def mock_meeting_upload(request: Request):
    """
    5장 회의록 자동화: 오디오 전사(Whisper) 및 구조화 회의록 추출 시뮬레이션
    """
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    card_id = str(uuid.uuid4())[:6]
    
    html_card = f"""
    <div class="meeting-card" id="meeting-{card_id}">
      <div class="meeting-header">
        <strong>🎙️ 주간 스프린트 & 아키텍처 점검</strong>
        <span class="route local">🔒 로컬 Whisper 전사</span>
      </div>
      <div class="meeting-body">
        <p><strong>일시:</strong> {now_str} | <strong>참석:</strong> 5인 전원</p>
        <p><strong>결정 사항:</strong> 12GB VRAM 제약을 고려해 Whisper와 Qwen3.5는 순차 큐로 실행하기로 합의함.</p>
        <p><strong>할 일:</strong> [김철수] MCP SQLite 권한 읽기 전용 잠금 확인 (내일까지)</p>
      </div>
    </div>
    """
    return HTMLResponse(content=html_card)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
