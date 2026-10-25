"""Direct commercial-model calls for readers without Hermes. Standard library only.

Provider order: TEAM_AGENT_PROVIDER, else the first key found among
ANTHROPIC_API_KEY (claude), OPENAI_API_KEY (openai), GEMINI_API_KEY (gemini).
TEAM_AGENT_MODEL overrides the default model. Keys are read from the
environment only and are never written to results or logs.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request

KEYS = {"claude": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
DEFAULT_MODELS = {"claude": "claude-sonnet-5-5", "openai": "gpt-5-mini", "gemini": "gemini-2.5-flash"}
SYSTEM = ("너는 마케팅 대행사 스튜디오 메리의 업무 에이전트다. 첨부 자료에 있는 사실만 쓰고, "
          "정해지지 않은 조건은 '확인 필요'로 남긴다. 다른 고객의 사실을 섞지 않는다.")


class ModelError(ValueError):
    def __init__(self, message, status=None, retry_after=None):
        super().__init__(message)
        self.status = status
        self.retry_after = retry_after
        self.provider = self.model = self.attempts = None


def provider():
    chosen = os.environ.get("TEAM_AGENT_PROVIDER")
    if chosen:
        if chosen not in KEYS:
            raise ModelError(f"TEAM_AGENT_PROVIDER는 {', '.join(KEYS)} 중 하나입니다.")
        if not os.environ.get(KEYS[chosen]):
            raise ModelError(f"{KEYS[chosen]} 환경 변수가 없습니다.")
        return chosen
    for name, key in KEYS.items():
        if os.environ.get(key):
            return name
    return None


def available():
    try:
        return provider() is not None
    except ModelError:
        return False


def _post(url, payload, headers, timeout):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        wait = error.headers.get("retry-after")
        found = re.search(r'"retryDelay":\s*"(\d+(?:\.\d+)?)s"', raw)
        retry_after = float(found.group(1)) if found else float(wait) if wait and wait.isdigit() else None
        raise ModelError(f"상용 API 오류 {error.code}: {raw[:300]}", error.code, retry_after) from None
    except urllib.error.URLError as error:
        raise ModelError(f"상용 API에 연결하지 못했습니다: {error.reason}") from None


def complete(prompt, *, json_output=False, max_tokens=8192, timeout=180, retries=4):
    """Return {'text', 'provider', 'model', 'usage', 'elapsed_seconds'}.

    usage keeps the provider's own token fields mapped to input/output/cache;
    fields the provider does not return stay None.
    """
    name = provider()
    if not name:
        raise ModelError("상용 API 키가 없습니다. ANTHROPIC_API_KEY·OPENAI_API_KEY·GEMINI_API_KEY 중 하나를 설정합니다.")
    key = os.environ[KEYS[name]]
    model = os.environ.get("TEAM_AGENT_MODEL") or DEFAULT_MODELS[name]
    started = time.monotonic()
    last = None
    for attempt in range(retries + 1):
        try:
            if name == "claude":
                body = _post("https://api.anthropic.com/v1/messages",
                             {"model": model, "max_tokens": max_tokens, "system": SYSTEM,
                              "messages": [{"role": "user", "content": prompt}]},
                             {"x-api-key": key, "anthropic-version": "2023-06-01"}, timeout)
                text = "".join(b.get("text", "") for b in body.get("content", []) if b.get("type") == "text")
                if body.get("stop_reason") == "max_tokens":  # 잘린 문서를 완성본으로 저장하지 않음
                    raise ModelError(f"출력 한도({max_tokens} 토큰)에서 응답이 잘렸습니다. 지시를 줄이거나 한도를 늘리세요.", status=400)
                u = body.get("usage", {})
                usage = {"input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
                         "cache_read_tokens": u.get("cache_read_input_tokens"),
                         "cache_write_tokens": u.get("cache_creation_input_tokens")}
            elif name == "openai":
                payload = {"model": model, "messages": [{"role": "system", "content": SYSTEM},
                                                        {"role": "user", "content": prompt}]}
                if json_output:
                    payload["response_format"] = {"type": "json_object"}
                body = _post("https://api.openai.com/v1/chat/completions", payload,
                             {"Authorization": f"Bearer {key}"}, timeout)
                text = body["choices"][0]["message"].get("content") or ""
                u = body.get("usage", {})
                usage = {"input_tokens": u.get("prompt_tokens"), "output_tokens": u.get("completion_tokens"),
                         "cache_read_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens"),
                         "cache_write_tokens": None}
            else:
                config = {"maxOutputTokens": max_tokens}
                if json_output:
                    config["responseMimeType"] = "application/json"
                body = _post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                             {"systemInstruction": {"parts": [{"text": SYSTEM}]},
                              "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                              "generationConfig": config},
                             {"x-goog-api-key": key}, timeout)
                candidates = body.get("candidates") or []
                if not candidates:
                    raise ModelError(f"응답 후보가 없습니다: {json.dumps(body.get('promptFeedback'), ensure_ascii=False)}")
                text = "".join(p.get("text", "") for p in candidates[0].get("content", {}).get("parts", []))
                if candidates[0].get("finishReason") == "MAX_TOKENS":
                    raise ModelError(f"출력 한도({max_tokens} 토큰)에서 응답이 잘렸습니다. 지시를 줄이거나 한도를 늘리세요.", status=400)
                u = body.get("usageMetadata", {})
                output = u.get("candidatesTokenCount")
                if output is not None and u.get("thoughtsTokenCount"):
                    output += u["thoughtsTokenCount"]
                usage = {"input_tokens": u.get("promptTokenCount"), "output_tokens": output,
                         "cache_read_tokens": u.get("cachedContentTokenCount"), "cache_write_tokens": None}
            if not text.strip():
                raise ModelError("빈 응답입니다.")
            return {"text": text, "provider": name, "model": model, "usage": usage,
                    "elapsed_seconds": round(time.monotonic() - started, 3), "attempts": attempt + 1}
        except ModelError as error:
            last = error
            if attempt >= retries:
                break
            if error.status == 429:  # 요청 한도: 분당 한도면 서버가 알려 준 시간만큼 기다림
                if (error.retry_after or 0) > 120 or "PerDay" in str(error):
                    break  # 하루 한도는 기다려도 풀리지 않으므로 바로 실패로 남김
                time.sleep(error.retry_after or 30 * (attempt + 1))
                continue
            if error.status is None or error.status >= 500:
                time.sleep(2 * (attempt + 1))
                continue
            break
    last.provider, last.model, last.attempts = name, model, attempt + 1  # 실패한 호출도 시도 수를 남긴다
    raise last


def strip_fence(text):
    """Remove one surrounding ``` fence that models often add."""
    match = re.match(r"^\s*```[a-zA-Z]*\n(.*)\n```\s*$", text, re.DOTALL)
    return match.group(1) if match else text


def repair_escapes(text):
    """Models sometimes emit invalid JSON escapes ('\\u12', '\\x'). Scan escapes left to right so valid
    pairs such as '\\\\' or '\\n' stay as they are and only invalid ones get their backslash doubled."""
    def fix(match):
        body = match.group(1)
        if body[0] in '"\\/bfnrt' or re.fullmatch(r"u[0-9a-fA-F]{4}", body):
            return match.group(0)
        return "\\\\" + body
    return re.sub(r'\\(u[0-9a-fA-F]{4}|.)', fix, text, flags=re.DOTALL)


def parse_json(text):
    text = strip_fence(text).strip()
    for candidate in (text, repair_escapes(text)):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    text = repair_escapes(text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ModelError("응답에서 JSON을 찾지 못했습니다.")
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as error:
        raise ModelError(f"응답 JSON을 읽지 못했습니다: {error}") from None


def attach(files):
    """Render files as attachments appended to a prompt. files: [(label, path)]."""
    parts = ["", "# 첨부 자료", "아래 파일 내용이 지시문에 나온 경로의 실제 내용이다. 파일 시스템에 접근할 수 없으므로 이 내용만 사용한다."]
    for label, path in files:
        parts += ["", f"## 파일: {label}", "```", path.read_text(encoding="utf-8").rstrip(), "```"]
    return "\n".join(parts)


if __name__ == "__main__":
    print(json.dumps({"provider": provider(), "model": os.environ.get("TEAM_AGENT_MODEL")
                      or DEFAULT_MODELS.get(provider() or "", None)}, ensure_ascii=False))
