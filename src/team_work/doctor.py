"""헤르메스 설정 가운데 이 예제에 영향을 주는 것을 읽어 보여 준다. 설정은 바꾸지 않는다.

입력: ~/.hermes(또는 HERMES_HOME)의 SOUL.md·skills/·config.yaml, 예제 폴더 경로
출력: 화면에 [정상]·[확인 필요] 줄과 다음에 할 일. 종료 코드는 확인 필요가 있으면 1
실행: 예제 폴더에서 `uv run main.py doctor`
"""

import os
import re
import shutil
import subprocess
from pathlib import Path


def _home():
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()


def _mcp_block(config_text, name):
    """config.yaml에서 name 서버 항목의 줄들을 돌려준다(YAML 해석 없이 들여쓰기로 자른다)."""
    lines = config_text.splitlines()
    for index, line in enumerate(lines):
        if line.strip().rstrip(":") == name and line.rstrip().endswith(":"):
            depth = len(line) - len(line.lstrip())
            block = [line]
            for rest in lines[index + 1:]:
                if rest.strip() and len(rest) - len(rest.lstrip()) <= depth:
                    break
                block.append(rest)
            return "\n".join(block)
    return None


def doctor(workspace, mcp=(), skills=(), soul=False, cron=False):
    work = Path(workspace).resolve()
    home = _home()
    lines, problems = [f"예제 폴더: {work}", f"헤르메스 설정: {home}"], 0

    # 1. 헤르메스 명령이 있는지 본다
    if shutil.which("hermes"):
        lines.append("[정상] hermes 명령을 찾았습니다.")
    else:
        lines.append("[확인 필요] hermes 명령이 없습니다. 1.2절 설치를 마쳤는지, 새 터미널을 열었는지 확인하세요.")
        problems += 1

    # 2. 이름·역할 규칙(SOUL.md)의 첫 줄을 보여 준다
    if soul:
        path = home / "SOUL.md"
        if path.is_file():
            first = next((x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()), "")
            lines.append(f"[정상] SOUL.md 첫 줄: {first[:80]}")
        else:
            lines.append("[확인 필요] ~/.hermes/SOUL.md가 없습니다. 1.3절의 이름 붙이기를 먼저 하세요.")
            problems += 1

    # 3. 설치된 스킬이 이 예제의 스킬과 같은지 본다
    for name in skills:
        installed = home / "skills" / name / "SKILL.md"
        local = next((p for p in (work / "output" / "skills" / name / "SKILL.md", work / "skills" / name / "SKILL.md")
                      if p.is_file()), None)
        if not installed.is_file():
            lines.append(f"[확인 필요] 스킬 {name}이 설치돼 있지 않습니다. 본문의 설치 명령을 먼저 실행하세요.")
            problems += 1
        elif local and installed.read_bytes() != local.read_bytes():
            lines.append(f"[확인 필요] 설치된 스킬 {name}이 이 예제의 {local.relative_to(work)}와 다릅니다. "
                         "이전 실습의 스킬일 수 있으니 내용을 비교한 뒤 다시 설치하세요.")
            problems += 1
        else:
            lines.append(f"[정상] 스킬 {name}이 설치돼 있습니다.")

    # 4. MCP 서버 등록이 이 예제 폴더를 가리키는지 본다(옛 폴더를 가리키면 조회가 실패한다)
    config = home / "config.yaml"
    text = config.read_text(encoding="utf-8") if config.is_file() else ""
    for name in mcp:
        block = _mcp_block(text, name)
        if block is None:
            lines.append(f"[안내] MCP 서버 {name}이 아직 등록되지 않았습니다. 본문의 hermes mcp add 명령으로 등록하세요.")
        elif re.search(re.escape(str(work)) + r"(?=[\s,\]'\"]|$)", block):
            lines.append(f"[정상] MCP 서버 {name}이 이 예제 폴더를 가리킵니다.")
        else:
            lines.append(f"[확인 필요] MCP 서버 {name}이 다른 폴더를 가리킵니다. "
                         f"hermes mcp remove {name}으로 지운 뒤 이 폴더에서 다시 등록하세요.")
            problems += 1

    # 5. 예약 작업 목록을 보여 준다(같은 이름의 예약이 남아 있으면 중복 실행된다)
    if cron and shutil.which("hermes"):
        try:
            done = subprocess.run(["hermes", "cron", "list"], capture_output=True, text=True, timeout=60, check=False)
            failed = done.returncode != 0
            listing = (done.stdout if not failed else done.stderr or done.stdout).strip()
        except subprocess.TimeoutExpired:
            failed, listing = True, "응답 없음(60초)"
        if failed:
            # 조회하지 못했으면 '예약 없음'으로 보지 않는다
            lines.append(f"[확인 필요] 예약 목록을 읽지 못했습니다: {listing[:200]}. hermes cron list를 직접 실행해 보세요.")
            problems += 1
        else:
            lines.append("[안내] 등록된 예약(hermes cron list). 연습이 끝난 예약은 hermes cron remove로 지웁니다:")
            lines += ["    " + x for x in (listing.splitlines() or ["(없음)"])[:15]]

    lines.append("점검 결과: " + ("이상 없음" if not problems else f"확인 필요 {problems}건"))
    print("\n".join(lines))
    return 1 if problems else 0


def register_parser(subparsers):
    p = subparsers.add_parser("doctor", help="헤르메스 설정(이름 규칙·스킬·MCP·예약) 점검, 변경 없음")
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--mcp", action="append", default=[])
    p.add_argument("--skill", action="append", default=[])
    p.add_argument("--soul", action="store_true")
    p.add_argument("--cron", action="store_true")
    p.set_defaults(func=lambda a: doctor(a.workspace, a.mcp, a.skill, a.soul, a.cron))
