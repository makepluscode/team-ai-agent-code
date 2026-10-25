"""Keep the existing commercial transport; require explicit current configuration."""

import importlib.util
import os
from pathlib import Path

TEAM_SYSTEM = (
    "너는 스튜디오 메리 팀의 내부 업무 에이전트다. 첨부 자료에 있는 사실만 쓰고, "
    "정해지지 않은 조건은 '확인 필요'로 남긴다."
)


def llm_module():
    # 상용 API 호출부(llm_api.py)를 호출마다 새로 읽는다. 호출부가 자체 시스템 프롬프트를 모듈 상태로 둔다.
    spec = importlib.util.spec_from_file_location(
        "team_work_llm_api", Path(__file__).resolve().parent / "llm_api.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call_commercial(system, prompt, *, json_output=False):
    if os.environ.get("TEAM_AGENT_PROVIDER", "claude") != "claude":
        raise ValueError("새 예제는 Claude 기준입니다. 다른 공급자 전환은 TODO(검증)입니다.")
    if not os.environ.get("ANTHROPIC_API_KEY") or not os.environ.get("TEAM_AGENT_MODEL"):
        raise ValueError(
            "ANTHROPIC_API_KEY와 확인한 TEAM_AGENT_MODEL을 환경 변수로 설정하세요. 모델 지원은 TODO(검증)입니다."
        )
    llm = llm_module()
    # Fresh module instance per call: the legacy runner keeps its own system prompt.
    llm.SYSTEM = TEAM_SYSTEM
    try:
        response = llm.complete(system + "\n\n" + prompt, json_output=json_output)
    except llm.ModelError:
        # Provider response bodies may echo supplied text. Do not expose them in logs.
        raise ValueError(
            "상용 호출에 실패했습니다. 입력·키는 기록하지 않았습니다. 설정과 공급자 상태를 확인하세요."
        ) from None
    return response


def parse_json(text):
    return llm_module().parse_json(text)
