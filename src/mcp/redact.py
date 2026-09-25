import re

PHONE_REGEX = re.compile(r'01[0-9]-?\d{3,4}-?\d{4}')
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
AMOUNT_REGEX = re.compile(r'\d{1,3}(,\d{3})*(만|천)?\s*원|\d{5,}\s*원|\b\d{7,}\b')

def redact_text(text: str) -> tuple[str, bool]:
    """
    민감 정보(전화번호, 이메일, 계약 금액 등)를 마스킹하여 안전한 텍스트로 변환한다.
    반환값: (가명화된 텍스트, 가명화 적용 여부)
    """
    redacted = False
    
    # 전화번호 마스킹
    if PHONE_REGEX.search(text):
        text = PHONE_REGEX.sub("[연락처-보안마스킹]", text)
        redacted = True
        
    # 이메일 마스킹
    if EMAIL_REGEX.search(text):
        text = EMAIL_REGEX.sub("[이메일-보안마스킹]", text)
        redacted = True
        
    # 금액 마스킹
    if AMOUNT_REGEX.search(text):
        text = AMOUNT_REGEX.sub("[금액-대외비]", text)
        redacted = True
        
    return text, redacted

def is_sensitive_query(query: str) -> bool:
    """
    질의 내용이 고객 DB, 계약, 개인정보와 관련된 3등급 데이터인지 판별한다.
    """
    sensitive_keywords = ["고객", "연락처", "전화번호", "계약", "금액", "단가", "인사", "급여", "매출"]
    return any(k in query for k in sensitive_keywords)
