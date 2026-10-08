"""[폐기 2026-10-08] 이 스크립트는 더 쓰지 않는다.

PIL로 영어 화면을 직접 그리던 방식이었고, 3부 9장 시절 설계(딥시크, 생성용 로컬 모델,
가명화, VRAM 12GB, 보안 논지)를 담고 있었다. 그 설계는 모두 폐기됐다.

지금은 `prototypes/dashboard_v2.html`을 실제로 렌더링해 찍는다.

    python3 prototypes/capture.py

그래야 시제품을 고치면 그림이 따라 바뀌고 둘이 어긋나지 않는다.
"""
import sys
sys.exit("폐기된 스크립트입니다. prototypes/capture.py를 쓰세요.")

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "captures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 폰트 로드 시도 (시스템 기본 폰트 또는 sans-serif)
def get_font(size: int, bold: bool = False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf" if bold else "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf" if bold else "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_badge(draw, x, y, text, is_local=True):
    bg_color = "#e3f4ee" if is_local else "#e6eefb"
    fg_color = "#0f7a5c" if is_local else "#2e5aa8"
    font = get_font(12, bold=True)
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + 16
    h = bbox[3] - bbox[1] + 10
    draw.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=bg_color)
    draw.text((x + 8, y + 4), text, fill=fg_color, font=font)
    return w, h

def render_ch01_dashboard():
    width, height = 1280, 720
    im = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(im)
    
    # 테두리 및 배경색
    draw.rectangle([0, 0, width, height], fill="#f4f5f7")
    
    # 좌측 사이드바
    draw.rectangle([0, 0, 220, height], fill="#ffffff", outline="#e3e6eb")
    f_brand = get_font(16, bold=True)
    draw.text((20, 24), "Team AI Agent", fill="#1c2330", font=f_brand)
    f_sub = get_font(12)
    draw.text((20, 48), "5-Person Team Ops", fill="#5f6b7a", font=f_sub)
    draw.line([(15, 75), (205, 75)], fill="#e3e6eb", width=1)
    
    menu_items = ["Dashboard (Live)", "Inquiry Inbox (3)", "Meeting Notes (2)", "Team Wiki (28)", "Security Audit"]
    y_menu = 95
    for i, item in enumerate(menu_items):
        f_m = get_font(13, bold=(i == 0))
        if i == 0:
            draw.rounded_rectangle([15, y_menu - 6, 205, y_menu + 26], radius=6, fill="#e6eefb")
            draw.text((25, y_menu), item, fill="#2e5aa8", font=f_m)
        else:
            draw.text((25, y_menu), item, fill="#5f6b7a", font=f_m)
        y_menu += 40
        
    # 사이드바 하단 상태
    draw.line([(15, height - 120), (205, height - 120)], fill="#e3e6eb", width=1)
    draw.ellipse([20, height - 100, 28, height - 92], fill="#0f7a5c")
    draw.text((36, height - 103), "System Online", fill="#1c2330", font=get_font(12, bold=True))
    draw.text((20, height - 75), "Local: qwen3.5:9b (GPU)", fill="#5f6b7a", font=get_font(11))
    draw.text((20, height - 55), "API: deepseek-flash", fill="#5f6b7a", font=get_font(11))
    draw.text((20, height - 35), "Hours: 09:00 - 18:00", fill="#5f6b7a", font=get_font(11))
    
    # 메인 상단 헤더
    draw.text((250, 24), "Monday Morning Team Dashboard", fill="#1c2330", font=get_font(22, bold=True))
    draw.text((250, 54), "Local LLM guards confidential data, while Hermes automates routine team workflows.", fill="#5f6b7a", font=get_font(13))
    
    draw_badge(draw, 960, 32, "🔒 Local LLM (Redaction & DB)", is_local=True)
    draw_badge(draw, 1145, 32, "☁️ Cloud API (Summary)", is_local=False)
    
    # KPI 4장 카드
    kpis = [
        ("Pending Inquiries", "3", "Night queue +2", "#a15c07"),
        ("Today Meetings", "2", "Whisper Transcribed", "#2e5aa8"),
        ("Team Wiki Knowledge", "28", "FTS5 Engine active", "#1c2330"),
        ("Data Protection Rate", "100%", "Blocked 14 / Leak 0", "#0f7a5c")
    ]
    x_kpi = 250
    for title, val, note, col in kpis:
        draw.rounded_rectangle([x_kpi, 85, x_kpi + 235, 175], radius=10, fill="#ffffff", outline="#e3e6eb")
        draw.text((x_kpi + 16, 98), title, fill="#5f6b7a", font=get_font(12))
        draw.text((x_kpi + 16, 120), val, fill=col, font=get_font(24, bold=True))
        draw.text((x_kpi + 16, 152), note, fill="#8a94a3", font=get_font(11))
        x_kpi += 252
        
    # 좌측 패널 (브리핑 & 알림 & 미팅)
    x_left = 250
    w_left = 540
    # 브리핑 카드
    draw.rounded_rectangle([x_left, 195, x_left + w_left, 350], radius=10, fill="#ffffff", outline="#e3e6eb")
    draw.text((x_left + 18, 208), "☀️ Morning Briefing (08:50 Auto-generated)", fill="#1c2330", font=get_font(14, bold=True))
    draw_badge(draw, x_left + w_left - 130, 206, "☁️ Cloud API", is_local=False)
    draw.line([(x_left, 240), (x_left + w_left, 240)], fill="#e3e6eb", width=1)
    brief_lines = [
        "• Urgent Inquiry: AI Solutions quote request - Check pricing table before reply.",
        "• Sprint Goal: Introduce FTS5 Wiki search and enforce MCP read-only mode.",
        "• Resource Check: 12GB VRAM - 6.8GB used by Qwen3.5:9B (5.2GB free)."
    ]
    y_b = 252
    for bl in brief_lines:
        draw.text((x_left + 18, y_b), bl, fill="#1c2330", font=get_font(12))
        y_b += 28
        
    # 미팅 카드
    draw.rounded_rectangle([x_left, 370, x_left + w_left, 690], radius=10, fill="#ffffff", outline="#e3e6eb")
    draw.text((x_left + 18, 383), "🎙️ Meeting Minutes (Whisper Local)", fill="#1c2330", font=get_font(14, bold=True))
    draw_badge(draw, x_left + w_left - 160, 381, "🔒 Local Whisper", is_local=True)
    draw.line([(x_left, 415), (x_left + w_left, 415)], fill="#e3e6eb", width=1)
    
    # 미팅 박스 1
    draw.rounded_rectangle([x_left + 16, 430, x_left + w_left - 16, 540], radius=8, fill="#f4f5f7", outline="#e3e6eb")
    draw.text((x_left + 30, 442), "Architecture & Security Review (10:00)", fill="#1c2330", font=get_font(13, bold=True))
    draw.text((x_left + 30, 465), "Decision: PII is strictly redacted on local GPU before cloud routing.", fill="#5f6b7a", font=get_font(12))
    draw.text((x_left + 30, 488), "Action: [Chulsoo] Verify SQLite MCP read-only locking by 18:00.", fill="#5f6b7a", font=get_font(12))
    draw.text((x_left + 30, 511), "Attendees: All 5 members | VRAM peak: 8.1GB (Whisper + Qwen)", fill="#8a94a3", font=get_font(11))

    # 미팅 박스 2
    draw.rounded_rectangle([x_left + 16, 555, x_left + w_left - 16, 665], radius=8, fill="#f4f5f7", outline="#e3e6eb")
    draw.text((x_left + 30, 567), "Quote Approval & Work Recipes (14:30)", fill="#1c2330", font=get_font(13, bold=True))
    draw.text((x_left + 30, 590), "Decision: Automated quotation draft approved via recipe script.", fill="#5f6b7a", font=get_font(12))
    draw.text((x_left + 30, 613), "Action: [Younghee] Final delivery of estimate PDF to client.", fill="#5f6b7a", font=get_font(12))
    draw.text((x_left + 30, 636), "Status: Completed (0 leaks detected in audit log)", fill="#0f7a5c", font=get_font(11, bold=True))

    # 우측 챗봇 패널
    x_chat = 810
    w_chat = 440
    draw.rounded_rectangle([x_chat, 195, x_chat + w_chat, 690], radius=10, fill="#ffffff", outline="#e3e6eb")
    draw.text((x_chat + 18, 208), "💬 Agent Chat & Delegation", fill="#1c2330", font=get_font(14, bold=True))
    draw.text((x_chat + w_chat - 140, 210), "FastAPI + HTMX", fill="#8a94a3", font=get_font(12))
    draw.line([(x_chat, 240), (x_chat + w_chat, 240)], fill="#e3e6eb", width=1)
    
    # 챗 영역
    draw.rectangle([x_chat, 241, x_chat + w_chat, 610], fill="#fafbfc")
    
    # 챗 메시지 1: Bot welcome
    draw.rounded_rectangle([x_chat + 16, 255, x_chat + w_chat - 40, 315], radius=8, fill="#ffffff", outline="#e3e6eb")
    draw_badge(draw, x_chat + 26, 263, "☁️ Cloud API", is_local=False)
    draw.text((x_chat + 26, 288), "Hello! How can I assist your team workflows today?", fill="#1c2330", font=get_font(12))

    # 챗 메시지 2: User question (DB query)
    draw.rounded_rectangle([x_chat + 60, 330, x_chat + w_chat - 16, 380], radius=8, fill="#2e5aa8")
    draw.text((x_chat + 72, 338), "You · 09:12", fill="#d4e2f8", font=get_font(11))
    draw.text((x_chat + 72, 355), "Query AI Solutions contract status and contact info", fill="#ffffff", font=get_font(12, bold=True))

    # 챗 메시지 3: Bot local redaction answer
    draw.rounded_rectangle([x_chat + 16, 395, x_chat + w_chat - 16, 520], radius=8, fill="#ffffff", outline="#0f7a5c")
    draw_badge(draw, x_chat + 26, 405, "🔒 Local LLM (SQLite MCP + Redacted)", is_local=True)
    reply_lines = [
        "Company: AI Solutions (Chulsoo Kim)",
        "Contact: [PHONE-PROTECTED] / [EMAIL-PROTECTED]",
        "Contract: LLM Infrastructure License",
        "Amount: [AMOUNT-CONFIDENTIAL] (Status: Complete)",
        "※ Policy: Confidential PII & amount redacted on local GPU."
    ]
    y_rep = 432
    for rl in reply_lines:
        col = "#0f7a5c" if "※" in rl else "#1c2330"
        draw.text((x_chat + 26, y_rep), rl, fill=col, font=get_font(11, bold=("※" in rl)))
        y_rep += 16

    # 챗 하단 입력창
    draw.line([(x_chat, 610), (x_chat + w_chat, 610)], fill="#e3e6eb", width=1)
    draw.rounded_rectangle([x_chat + 16, 625, x_chat + w_chat - 90, 665], radius=6, fill="#ffffff", outline="#2e5aa8")
    draw.text((x_chat + 26, 638), "Ask agent (e.g. Wiki search, Quote)...", fill="#8a94a3", font=get_font(12))
    draw.rounded_rectangle([x_chat + w_chat - 80, 625, x_chat + w_chat - 16, 665], radius=6, fill="#2e5aa8")
    draw.text((x_chat + w_chat - 62, 638), "Send", fill="#ffffff", font=get_font(12, bold=True))

    out_path = OUTPUT_DIR / "ch01_dashboard_full.png"
    im.save(out_path, "PNG")
    print(f"Generated: {out_path}")

def render_ch02_chat_response():
    width, height = 900, 500
    im = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(im)
    draw.rectangle([0, 0, width, height], fill="#f4f5f7")
    
    # 윈도우 프레임
    draw.rounded_rectangle([20, 20, width - 20, height - 20], radius=10, fill="#ffffff", outline="#e3e6eb")
    draw.text((40, 36), "Chapter 2: Minimal FastAPI + HTMX Chatbot", fill="#1c2330", font=get_font(15, bold=True))
    draw.text((40, 60), "Testing initial echo and cloud API connectivity without local model", fill="#5f6b7a", font=get_font(12))
    draw.line([(20, 85), (width - 20, 85)], fill="#e3e6eb", width=1)
    
    # 대화 버블 1: User '안녕'
    draw.rounded_rectangle([width - 320, 115, width - 40, 175], radius=8, fill="#2e5aa8")
    draw.text((width - 305, 126), "User · 10:02:15", fill="#d4e2f8", font=get_font(11))
    draw.text((width - 305, 145), "Hello! 에이전트 동작 확인", fill="#ffffff", font=get_font(13, bold=True))
    
    # 대화 버블 2: Bot '안녕' 응답
    draw.rounded_rectangle([40, 200, width - 200, 300], radius=8, fill="#fafbfc", outline="#e3e6eb")
    draw_badge(draw, 55, 212, "☁️ Cloud API (Echo / Hermes)", is_local=False)
    draw.text((195, 214), "Bot · 10:02:16", fill="#5f6b7a", font=get_font(11))
    draw.text((55, 245), "안녕하세요! 헤르메스 팀 에이전트 뼈대 서비스입니다.", fill="#1c2330", font=get_font(13, bold=True))
    draw.text((55, 270), "FastAPI + HTMX 비동기 스왑이 정상 작동하며 웹 대시보드가 준비되었습니다.", fill="#5f6b7a", font=get_font(12))

    # 입력 폼
    draw.rounded_rectangle([40, 410, width - 140, 455], radius=8, fill="#ffffff", outline="#e3e6eb")
    draw.text((55, 425), "다음 질문을 입력하세요...", fill="#8a94a3", font=get_font(12))
    draw.rounded_rectangle([width - 125, 410, width - 40, 455], radius=8, fill="#2e5aa8")
    draw.text((width - 100, 425), "전송", fill="#ffffff", font=get_font(13, bold=True))

    out_path = OUTPUT_DIR / "ch02_chat_response.png"
    im.save(out_path, "PNG")
    print(f"Generated: {out_path}")

def render_ch04_local_redaction():
    width, height = 900, 520
    im = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(im)
    draw.rectangle([0, 0, width, height], fill="#f4f5f7")
    
    # 윈도우 프레임
    draw.rounded_rectangle([20, 20, width - 20, height - 20], radius=10, fill="#ffffff", outline="#e3e6eb")
    draw.text((40, 36), "Chapter 4: Local LLM Redaction & SQLite MCP", fill="#1c2330", font=get_font(15, bold=True))
    draw.text((40, 60), "Verifying confidential data masking before external API delegation", fill="#5f6b7a", font=get_font(12))
    draw.line([(20, 85), (width - 20, 85)], fill="#e3e6eb", width=1)
    
    # DB 원본 데이터 표시
    draw.rounded_rectangle([40, 105, width - 40, 205], radius=8, fill="#fdf1dc", outline="#a15c07")
    draw.text((55, 118), "⚠️ SQLite Internal DB Raw Data (Never leaves local server):", fill="#a15c07", font=get_font(12, bold=True))
    draw.text((55, 142), "Customer: Chulsoo Kim (AI Solutions) | Phone: 010-1234-5678 | Email: chulsoo.kim@aisol.com", fill="#1c2330", font=get_font(12))
    draw.text((55, 168), "Contract: LLM Infrastructure License | Amount: 45,000,000 KRW | Status: Complete", fill="#1c2330", font=get_font(12))
    
    # 화살표 및 필터
    draw.text((width // 2 - 120, 220), "⬇️ Local Qwen3.5:9B Redaction Filter ⬇️", fill="#0f7a5c", font=get_font(13, bold=True))
    
    # 가명화된 텍스트 표시
    draw.rounded_rectangle([40, 255, width - 40, 365], radius=8, fill="#e3f4ee", outline="#0f7a5c")
    draw.text((55, 268), "🔒 Redacted Output (Safe for Dashboard & Cloud Delegation):", fill="#0f7a5c", font=get_font(12, bold=True))
    draw.text((55, 295), "Customer: [CUSTOMER-A] | Contact: [PHONE-MASKED] | Email: [EMAIL-MASKED]", fill="#1c2330", font=get_font(12, bold=True))
    draw.text((55, 325), "Contract: LLM Infrastructure License | Amount: [AMOUNT-CONFIDENTIAL] | Status: Complete", fill="#1c2330", font=get_font(12, bold=True))

    # 감사 로그 확인
    draw.rounded_rectangle([40, 385, width - 40, 480], radius=8, fill="#ffffff", outline="#e3e6eb")
    draw.text((55, 398), "Audit Verification (ch08 Leak Checker):", fill="#5f6b7a", font=get_font(12, bold=True))
    draw.text((55, 425), "Phone match count in cloud payload: 0 (PASSED)", fill="#0f7a5c", font=get_font(12))
    draw.text((55, 448), "Amount match count in cloud payload: 0 (PASSED)", fill="#0f7a5c", font=get_font(12))

    out_path = OUTPUT_DIR / "ch04_local_redaction.png"
    im.save(out_path, "PNG")
    print(f"Generated: {out_path}")

if __name__ == "__main__":
    render_ch01_dashboard()
    render_ch02_chat_response()
    render_ch04_local_redaction()
    print("All captures rendered successfully.")
