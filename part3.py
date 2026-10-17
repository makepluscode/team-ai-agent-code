#!/usr/bin/env python3
"""Part 3 (chapters 7~9) prepared exercises. Data in ch07~ch09/start, prompts in chNN/prompts. Standard-library pipeline; models are optional.
Reference mode is an authored fixture, never inference or evaluation evidence.
Judgment runs locally (Laya via Ollama or Python) or on a commercial API
(--transport api) with the same result format.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0,str(BASE))
CHAPTERS=['ch07','ch08','ch09']
import llm  # noqa: E402
import wiki as team_wiki  # noqa: E402

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def save(path, value):
    path=Path(path)
    if path.exists():
        raise ValueError(f'기존 결과를 보존합니다: {path}. 새 작업 폴더를 사용합니다.')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def hashes(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}

def prepare(work,wiki_from='ch06',with_wiki=True):
    work=Path(work).resolve()
    if work.exists() and any(work.iterdir()):
        raise ValueError('빈 작업 폴더에서 시작합니다. 이전 결과는 보존합니다.')
    work.mkdir(parents=True,exist_ok=True)
    for chapter in CHAPTERS:
        shutil.copytree(BASE/chapter/'start',work/'input',dirs_exist_ok=True)
        shutil.copytree(BASE/chapter/'start',work/'model-input',dirs_exist_ok=True)
    (work/'model-input/comparison-structure.json').unlink(missing_ok=True)
    rows=read(work/'input/inquiries.json')
    target=work/'model-input/inquiries.json'
    target.write_text(json.dumps([{k:r[k] for k in ['id','client_id','campaign_id','body']} for r in rows],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (work/'output').mkdir();(work/'prompts').mkdir()
    if with_wiki:team_wiki.init(work/'wiki',wiki_from)
    for p in sorted(BASE.glob('ch0[789]/prompts/*.txt')):
        text=p.read_text(encoding='utf-8').replace('{{INPUT}}',str(work/'model-input')).replace('{{OUTPUT}}',str(work/'output')).replace('{{TRANSCRIPT}}',str(work/'output/transcript.json'))
        (work/'prompts'/p.name).write_text(text,encoding='utf-8')
    save(work/'input-hashes.json',{'input':hashes(work/'input'),'model-input':hashes(work/'model-input')})
    print(f'준비 완료: {work}'+(f' (연습 위키: {work/"wiki"}, {wiki_from} 끝 상태)' if with_wiki else ''))
    return work

def unchanged(work):
    original=read(work/'input-hashes.json')
    if any(hashes(work/key)!=original[key] for key in original):
        raise ValueError('입력이 변경됐습니다. 원자료와 대조하고 새 폴더에서 복구합니다.')

def inquiry(work,ident):
    row=next((r for r in read(work/'input/inquiries.json') if r['id']==ident),None)
    if row is None: raise ValueError('문의 ID를 확인합니다.')
    return row

def versioned(work,name,version=None):
    path=work/'input'/(name if not version else name.replace('.json',f'.{version}.json'))
    if not path.is_file():raise ValueError(f'판이 없습니다: {path.name}')
    return read(path)

def request_body(work,ident,version=None):
    row=inquiry(work,ident)
    return {'model':'laya:322m-multilingual-mlx-fp16','state':{k:row[k] for k in ['body','client_id','campaign_id']},'questions':versioned(work,'questions.json',version)}

LAST_CALL={}  # 응답을 해석하기 전에 호출 기록을 남긴다(해석·검증에 실패한 호출도 사용량 집계에 포함)

def commercial_decide(work,body,criteria=None):
    """Same questions to a commercial model; converted to the Laya answer format."""
    prompt=(BASE/'ch07/prompts/ch07-classify.txt').read_text(encoding='utf-8').replace('{{INPUT}}','첨부 자료')
    prompt+='\n\n# 판정 질문(questions.json)\n'+json.dumps(body['questions'],ensure_ascii=False,indent=2)
    prompt+='\n\n# 문의\n'+json.dumps(body['state'],ensure_ascii=False,indent=2)
    if criteria:
        prompt+='\n\n# 팀의 판단 기준 페이지(위키)\n상태가 적용·승인인 기준만 판정에 반영해 줘.\n'+Path(criteria).read_text(encoding='utf-8')
    shape={k:({'choice':'선택지 이름','confidence':0.0} if q['type']=='choice' else {'score':0} if q['type']=='score' else {'noul':0.0})
           for k,q in body['questions'].items() if not k.startswith('_')}
    prompt+='\n\n# 답하는 형식\nJSON 하나로만 답해 줘. 형식: '+json.dumps({**shape,'evidence':'본문 구절'},ensure_ascii=False)
    LAST_CALL.clear()  # 이전 문의의 기록을 다음 문의에 섞지 않는다
    try:
        call=llm.complete(prompt,json_output=True,max_tokens=4096)
    except llm.ModelError as error:
        LAST_CALL.update({'processing_location':'cloud','provider':error.provider,'model':error.model,'usage':None,'attempts':error.attempts,'http':'failed'})
        raise
    LAST_CALL.update({'processing_location':'cloud','provider':call['provider'],'model':call['model'],'usage':call['usage'],'attempts':call.get('attempts')})
    raw=llm.parse_json(call['text']);answers={}
    for key,q in body['questions'].items():
        if key.startswith('_'):continue
        a=raw.get(key)
        if not isinstance(a,dict):answers[key]={'type':'refusal'};continue
        if q['type']=='choice':answers[key]={'type':'choice','choice':a.get('choice'),'confidence':a.get('confidence'),'probabilities':None}
        elif q['type']=='score':answers[key]={'type':'score','score':a.get('score')}
        else:answers[key]={'type':'noul','noul':a.get('noul')}
    return {'answers':answers,'evidence':raw.get('evidence'),'model':call['model'],'usage':call['usage']},call

def decide(work,ident,reference=False,transport='ollama',version=None,criteria=None):
    row=inquiry(work,ident);body=request_body(work,ident,version)
    target=work/'output/decisions'/(f'{ident}.{version}.json' if version else f'{ident}.json')
    if target.exists(): raise ValueError('같은 문의의 기존 판정을 보존합니다.')
    started=time.monotonic();call=None
    if reference:
        expected=row['expected']
        answers={k:{'type':'choice','choice':expected[k],'confidence':0.92,'probabilities':None} for k in ['category','role']}
        answers.update(urgency={'type':'score','score':expected['urgency']},contract_stop={'type':'noul','noul':1.0 if expected['contract_stop'] else 0.0})
        result={'answers':answers,'model':None,'usage':None}
    elif transport=='api':
        result,call=commercial_decide(work,body,criteria)
    elif transport=='python':
        import laya
        agent=laya.load('convaiinnovations/laya-multilingual',device='cpu')
        result=agent.predict(body['state'],body['questions'])
    else:
        payload=json.dumps(body,ensure_ascii=False).encode('utf-8')
        req=urllib.request.Request('http://127.0.0.1:11434/v1/systemone',data=payload,headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=120) as response:
            result=json.load(response)
    cloud=transport=='api' and not reference
    result['_meta']={'inquiry_id':ident,'client_id':row['client_id'],'campaign_id':row['campaign_id'],
                     'data_origin':'authored-fixture' if reference else 'measured-cloud' if cloud else 'measured-local',
                     'processing_location':'cloud' if cloud else 'local',
                     'provider':'fixture' if reference else call['provider'] if cloud else 'laya',
                     'model_requested':None if reference else call['model'] if cloud else body['model'] if transport=='ollama' else 'convaiinnovations/laya-multilingual',
                     'questions_version':(body['questions'].get('_version') or {}).get('version',1),
                     'criteria_page':str(criteria) if criteria else None,
                     'usage':call['usage'] if cloud else None,'attempts':call.get('attempts') if cloud else None,
                     'elapsed_seconds':None if reference else round(time.monotonic()-started,3),
                     'timing_scope':'request round trip' if cloud else 'load-and-request; cold/warm split not measured','cost_usd':None}
    save(target,result)
    return result

def number(value,lo,hi):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not lo<=value<=hi:
        raise ValueError('판정 숫자가 누락됐거나 범위를 벗어났습니다.')
    return value

def routing(work,ident,version=None):
    name=f'{ident}.{version}.json' if version else f'{ident}.json'
    decision=read(work/'output/decisions'/name);row=inquiry(work,ident)
    if decision.get('_meta',{}).get('inquiry_id')!=ident: raise ValueError('문의와 판정 ID가 다릅니다.')
    rules=versioned(work,'rules.json',version);answers=decision.get('answers',{});reasons=[]
    selected={};questions=versioned(work,'questions.json',version)
    for key in ['category','role']:
        a=answers.get(key,{})
        if a.get('type')!='choice' or a.get('choice') not in questions[key]['criteria']:
            selected[key]=None;reasons.append(f'{key}: 거부·미반환·알 수 없는 선택지');continue
        selected[key]=a['choice']
        try:
            confidence=number(a.get('confidence'),0,1)
            if confidence<float(rules['confidence_threshold']): reasons.append(f'{key}: 임계값 미달')
        except ValueError: reasons.append(f'{key}: 신뢰도 확인 필요')
    try:
        urgency=number(answers.get('urgency',{}).get('score'),0,2)
        risk=number(answers.get('contract_stop',{}).get('noul'),0,1)
        if urgency>=1.5 or risk>=float(rules['risk_review_threshold']):reasons.append('긴급 대응 또는 계약 중단 표현 확인')
    except ValueError: reasons.append('긴급도 또는 계약 중단 판정 확인 필요')
    if selected.get('category')=='클레임': reasons.append('클레임 원문과 대응 확인')
    if selected.get('category') in ('일정','견적'): reasons.append('일정·견적 조건 확인')
    collaborator=(answers.get('collaborator') or {}).get('choice')
    if collaborator and collaborator!='없음' and collaborator!=selected.get('role'):
        selected['collaborator']=collaborator;reasons.append(f'협업 직군 {collaborator} 확인')
    confirm_owner=None;applied=[]
    for rule in rules.get('criteria_rules',[]):
        if rule.get('status')!='적용':continue
        if rule['when']=='quote_sku_not_in_price_list' and offlist(work,ident):
            reasons.append(rule['reason']);confirm_owner=rule['confirm_owner'];applied.append(rule['id'])
    synthetic=decision.get('_meta',{}).get('data_origin') not in ('measured-local','measured-cloud')
    result={'inquiry_id':ident,'client_id':row['client_id'],'campaign_id':row['campaign_id'],**selected,
            'confirm_owner':confirm_owner,'criteria_applied':applied,
            'status':'review_required' if reasons else 'assignment_proposed','reasons':reasons,
            'person_assigned':None,'external_assignment':False,'simulation':synthetic,
            'processing_location':decision.get('_meta',{}).get('processing_location'),
            'threshold_status':rules['threshold_status'],'source':f'decisions/{name}'}
    save(work/'output/routing'/name,result);return result

def offlist(work,ident):
    req=next((r for r in read(work/'input/quote-requests.json') if r['inquiry_id']==ident),None)
    if not req:return False
    known={p['sku'] for p in read(work/'input/price-list.json')}
    return any(item['sku'] not in known for item in request_items(req))

def request_items(req):
    return req.get('items') or [{'sku':req.get('sku'),'quantity':req.get('quantity')}]

def estimate(work,ident):
    row=inquiry(work,ident);rules=read(work/'input/rules.json')
    req=next((r for r in read(work/'input/quote-requests.json') if r['inquiry_id']==ident),None)
    base={'inquiry_id':ident,'client_id':row['client_id'],'currency':'KRW','status':'review_required','total_krw':None,'send_allowed':False}
    if not req:return {**base,'reason':'견적 요청과 수량을 확인합니다.'}
    if not (work/'output/team.db').is_file(): raise ValueError('먼저 database로 조회용 DB를 준비합니다.')
    lines=[]
    with readonly(work/'output/team.db') as db:
        for item in request_items(req):
            found=db.execute('SELECT sku,name,unit_price_krw FROM prices WHERE sku=?',(item['sku'],)).fetchone()
            price=dict(found) if found else None
            q=item['quantity']
            if price is None or isinstance(q,bool) or not isinstance(q,int) or not 1<=q<=rules['quantity_limit']:
                return {**base,'reason':'단가표 밖 항목 또는 미정·잘못된 수량입니다.','problem_item':item}
            lines.append({'sku':item['sku'],'name':price['name'],'quantity':q,'unit_price_krw':price['unit_price_krw'],'amount_krw':price['unit_price_krw']*q})
    discount=Decimal(str(req['discount']));tax_rate=Decimal(rules['tax_rate'])
    if not 0<=discount<=1 or not 0<=tax_rate<=1: raise ValueError('할인·세율 범위를 확인합니다.')
    subtotal=sum(Decimal(l['unit_price_krw'])*l['quantity'] for l in lines)
    supply=(subtotal*(1-discount)).quantize(Decimal('1'),rounding=ROUND_HALF_UP)
    tax=(supply*tax_rate).quantize(Decimal('1'),rounding=ROUND_HALF_UP)
    total=supply+tax
    single={'sku':lines[0]['sku'],'quantity':lines[0]['quantity'],'unit_price_krw':lines[0]['unit_price_krw']} if len(lines)==1 else {}
    return {**base,**single,'lines':lines,'subtotal_krw':int(subtotal),
            'discount':str(discount),'supply_krw':int(supply),'tax_krw':int(tax),'total_krw':int(total),
            'reason':'고액 금액 확인' if total>=rules['high_quote_krw'] else '금액·수량·세금의 사람 확인',
            'price_source':'output/team.db/prices (원본: input/price-list.json)','data_origin':'synthetic-business-data'}

def build_database(work):
    path=work/'output/team.db'
    if path.exists():raise ValueError('기존 DB를 보존합니다.')
    with sqlite3.connect(path) as db:
        db.executescript('CREATE TABLE inquiries(id TEXT PRIMARY KEY, client_id TEXT, body TEXT); CREATE TABLE customers(id TEXT PRIMARY KEY, name TEXT); CREATE TABLE prices(sku TEXT PRIMARY KEY, name TEXT, unit_price_krw INTEGER);')
        db.executemany('INSERT INTO inquiries VALUES(?,?,?)',[(r['id'],r['client_id'],r['body']) for r in read(work/'input/inquiries.json')])
        db.executemany('INSERT INTO customers VALUES(?,?)',[(r['id'],r['name']) for r in read(work/'input/customers.json')])
        db.executemany('INSERT INTO prices VALUES(?,?,?)',[(r['sku'],r['name'],r['unit_price_krw']) for r in read(work/'input/price-list.json')])
    return path

def readonly(path):
    db=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    return db

def evaluation(rows,reference=False,development=False):
    if not rows:raise ValueError('판정 기록이 없습니다.')
    if len({r['id'] for r in rows})!=len(rows):raise ValueError('중복 문의 ID입니다.')
    if development:
        if any(r.get('data_origin')!='measured' for r in rows):raise ValueError('개발 묶음 측정에는 실제 판정 기록만 씁니다.')
        correct={key:sum(r['expected'].get(key)==r['predicted'].get(key) and r['predicted'].get(key) is not None for r in rows) for key in ['category','role']}
        return {'mode':'development-measurement','count':len(rows),'correct_count':correct,
                'development_accuracy':{key:round(value/len(rows),3) for key,value in correct.items()},'accuracy':None,
                'review_required':sum(r.get('review_required') is True for r in rows),
                'note':'개발용 미리보기 30건(정답 초안)에 대한 측정입니다. 임계값 조정용이며 평가 결과(정확도)로 쓰지 않습니다.'}
    if not reference and any(r.get('data_origin')!='measured' or r.get('split')!='evaluation' for r in rows):
        raise ValueError('실측 평가 묶음만 품질 집계에 사용합니다. 초안·비교용 자료는 --reference로 구조만 확인합니다.')
    for row in rows:
        if not isinstance(row.get('expected'),dict) or not isinstance(row.get('predicted'),dict):raise ValueError('정답·판정 형식을 확인합니다.')
    correct={key:sum(r['expected'].get(key)==r['predicted'].get(key) and r['predicted'].get(key) is not None for r in rows) for key in ['category','role']}
    return {'mode':'reference-structure-only' if reference else 'measured-evaluation','count':len(rows),'correct_count':correct,
            'accuracy':None if reference else {key:value/len(rows) for key,value in correct.items()},
            'note':'초고 자료의 집계는 실제 판정 성능이 아닙니다. 유형별 성적·이관·오판·긴급도 오차·시간·비용 상세 비교는 작성 예정입니다.'}

def extract_minutes(work,reference=False,engine=None):
    transcript=work/'output/transcript.json'
    if not transcript.exists():raise ValueError('먼저 실제 전사 또는 비교용 전사문을 준비합니다.')
    target=work/'output/minutes.json'
    if target.exists():raise ValueError('기존 회의록을 보존합니다.')
    if reference:
        result=read(BASE/'ch09/completed/minutes.json');save(target,result)
    elif (engine or ('hermes' if shutil.which('hermes') else 'api' if llm.available() else 'hermes'))=='api':
        prompt=(work/'prompts/ch09-extract.txt').read_text(encoding='utf-8')
        prompt+='\n\n# 답하는 형식\n파일을 직접 저장할 수 없으니 minutes.json에 들어갈 JSON 하나로만 답해 줘. version은 정수, decisions의 각 항목은 id·status·value·evidence(·supersedes)를 가진다.'
        prompt+=llm.attach([('meeting.json',work/'model-input/meeting.json'),('transcript.json',transcript)])
        LAST_CALL.clear()
        try:
            call=llm.complete(prompt,json_output=True)
        except llm.ModelError as error:
            LAST_CALL.update({'processing_location':'cloud','provider':error.provider,'model':error.model,'usage':None,'attempts':error.attempts,'http':'failed'})
            raise
        meta={'data_origin':'measured-cloud','processing_location':'cloud','provider':call['provider'],'model':call['model'],'usage':call['usage'],'elapsed_seconds':call['elapsed_seconds'],'attempts':call.get('attempts')}
        LAST_CALL.update(meta)  # 파싱·검증이 실패해도 호출 기록은 남긴다
        result=normalize_minutes(llm.parse_json(call['text']))
        result['_meta']=meta
        save(target,result)
    else:
        command=shutil.which('hermes')
        if not command:raise ValueError('헤르메스 설치·상용 모델 연결을 확인합니다. API 키가 있으면 --engine api를 씁니다.')
        subprocess.run([command,'chat','--oneshot','--query-file',str(work/'prompts/ch09-extract.txt')],cwd=work,check=True)
    result=read(target)
    validate_minutes(result,read(work/'input/meeting.json'),read(transcript))
    return result

def normalize_minutes(result):
    """Accept decisions grouped by status ({'confirmed':[...]}) by flattening; the status field is kept per item."""
    d=result.get('decisions')
    if isinstance(d,dict):
        flat=[]
        for status,items in d.items():
            for item in items or []:
                if isinstance(item,dict):flat.append({'status':status,**item})
        result['decisions']=flat
    return result

def squash(text):
    return re.sub(r'[\s\W_]+','',str(text))

def validate_minutes(result,meeting,transcript=None):
    if result.get('meeting_id')!=meeting['id'] or result.get('source_event_id')!=meeting['source_event_id']:raise ValueError('회의 또는 출처 사건 ID가 다릅니다.')
    for key in ['decisions','cancelled','actions','unknown']:
        if not isinstance(result.get(key),list):raise ValueError(f'회의록 필수 목록 확인: {key}')
    if not isinstance(result.get('version'),int) or result['version']<1:raise ValueError('문서 버전을 확인합니다.')
    if not result['decisions']:raise ValueError('결정이 하나도 없습니다. 전사문과 추출 결과를 확인합니다.')
    for d in result['decisions']:
        if d.get('status') not in ['confirmed','tentative','cancelled'] or not d.get('evidence') or not d.get('value') or not d.get('id'):raise ValueError('결정의 상태·근거·ID·내용을 확인합니다.')
    for a in result['actions']:
        if not isinstance(a,dict) or not a.get('task') or not a.get('role'):raise ValueError('할 일마다 task·role이 필요합니다.')
    if transcript is not None:
        spoken=squash(' '.join(seg.get('text','') for seg in transcript.get('segments',[])))
        missing=[d['id'] for d in result['decisions'] if squash(d['evidence']) not in spoken]
        if missing:raise ValueError(f'근거 문장이 전사문에 없습니다: {", ".join(missing)}')
    return result

PRIVATE=[(re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'),'[삭제: 개인정보]'),(re.compile(r'01[016789]-?\d{3,4}-?\d{4}'),'[삭제: 개인정보]')]

def redact(text,extra=()):
    for pattern,mark in PRIVATE:text=pattern.sub(mark,text)
    for word in extra:
        if word:text=text.replace(word,'[삭제: 개인정보]')
    return text

def stamp(value):
    if value is None:return '시간 미측정'
    return f'{int(value)//60:02d}:{int(value)%60:02d}'

def publish_bundle(work):
    meeting=read(work/'input/meeting.json')
    result=validate_minutes(read(work/'output/minutes.json'),meeting,read(work/'output/transcript.json'))
    target=work/'output/wiki-input'
    if target.exists():raise ValueError('기존 게시 대기 자료를 보존합니다.')
    target.mkdir()
    transcript_path=work/'output/transcript.json'
    shutil.copy2(transcript_path,target/'transcript.json')
    save(target/'minutes.json',result)
    transcript=read(transcript_path)
    full_hash=hashlib.sha256(transcript_path.read_bytes()).hexdigest()
    audio=work/'input/audio/meeting-smoke.mp3'
    audio_hash=hashlib.sha256(audio.read_bytes()).hexdigest() if audio.is_file() else None
    day=meeting['recorded_on'].replace('-','');prefix=f"{day}_{meeting['client_id']}_{meeting['campaign_id']}"
    head=(f"---\nmeeting_id: {result['meeting_id']}\nclient: {meeting['client_id']}\ncampaign: {meeting['campaign_id']}\n"
          f"date: {meeting['recorded_on']}\nkind: meeting\nsource_event: {result['source_event_id']}\nversion: {result['version']}\n"
          f"status: publication_pending\nrecording_sha256: {audio_hash or '확인 필요'}\nrecording_location: 위키 밖(녹음한 참석자의 컴퓨터)\n"
          f"transcript_full_sha256: {full_hash}\nconfirmed_by: 확인 필요\n---\n\n")
    text=head+'# 봉봉소프트 회의 결정\n\n## 결정\n\n'
    for d in result['decisions']:
        text+=f"- [{d['status']}] {d['id']}: {d['value']} (근거: {d['evidence']})"+(f" (대체: {d['supersedes']})" if d.get('supersedes') else '')+'\n'
    text+='\n## 취소\n\n'+''.join(f'- {c}\n' for c in result['cancelled'] or ['없음'])
    text+='\n## 할 일\n\n'+''.join(f"- {a.get('role')}: {a.get('task')} (기한: {a.get('due') or '확인 필요'})\n" for a in result['actions'] or [{'role':'없음','task':'','due':None}])
    text+='\n## 미정 조건\n\n'+''.join(f'- {u} — 확인 필요\n' for u in result['unknown'] or ['없음'])
    text+=f"\n전사문 원본: raw/{prefix}_transcript.md. 기한·담당·금액과 원문을 사람이 확인한 뒤 status를 confirmed로 바꿔 위키 원본으로 넣습니다. 이전 판은 보존합니다.\n"
    (target/'meeting.md').write_text(text,encoding='utf-8')
    (target/f'{prefix}_meeting.md').write_text(text,encoding='utf-8')
    extra=[]
    if (work/'input/redact.txt').is_file():extra=[l.strip() for l in (work/'input/redact.txt').read_text(encoding='utf-8').splitlines() if l.strip()]
    lines=[]
    for seg in transcript['segments']:
        body=redact(seg['text'],extra).strip()
        span=f"[{stamp(seg.get('start'))}~{stamp(seg.get('end'))}]" if seg.get('start') is not None else '[시간 미측정]'
        lines.append(f'{span} {body}')
    removed=sum(l.count('[삭제: 개인정보]') for l in lines)
    missing=[d['id'] for d in result['decisions'] if d['evidence'] not in '\n'.join(lines)]
    tr=(f"---\nmeeting_id: {result['meeting_id']}\nclient: {meeting['client_id']}\ncampaign: {meeting['campaign_id']}\n"
        f"date: {meeting['recorded_on']}\nkind: transcript\nredacted: true\nredactions: {removed}\n"
        f"full_transcript_sha256: {full_hash}\nfull_transcript_location: 위키 밖\n---\n\n"
        "개인정보와 업무 밖 발언은 [삭제: 개인정보]로 바꿨습니다. 자동 삭제는 주소·전화번호만 찾으므로 이름과 업무 밖 발언은 사람이 확인합니다.\n\n")
    (target/f'{prefix}_transcript.md').write_text(tr+'\n'.join(lines)+'\n',encoding='utf-8')
    return {'folder':str(target),'status':'publication_pending','external_writes':False,'source_transcript':'transcript.json','wiki_built':False,
            'wiki_raw':[f'{prefix}_meeting.md',f'{prefix}_transcript.md'],'redactions':removed,'evidence_missing_after_redaction':missing}

def confirm_bundle(work,by):
    """Human step: after checking, mark the meeting raw as confirmed."""
    folder=work/'output/wiki-input'
    files=sorted(folder.glob('*_meeting.md'))
    if not files:raise ValueError('먼저 publish로 게시 대기 묶음을 만듭니다.')
    for path in files:
        text=path.read_text(encoding='utf-8')
        if 'status: publication_pending' not in text:raise ValueError(f'이미 확인했거나 형식이 다릅니다: {path.name}')
        path.write_text(text.replace('status: publication_pending','status: confirmed').replace('confirmed_by: 확인 필요',f'confirmed_by: {by}'),encoding='utf-8')
    return {'confirmed':[p.name for p in files],'confirmed_by':by}

# ---- 8.3 human review and 8.4 review cases ----

def state_record(work,ident):
    routed=read(work/'output/routing'/f'{ident}.json')
    quote=work/'output/quotes'/f'{ident}.json'
    history=[{'version':1,'actor':'model','by':routed.get('processing_location') or 'unknown','at':datetime.now().astimezone().isoformat(timespec='seconds'),
              'category':routed.get('category'),'role':routed.get('role'),'collaborator':routed.get('collaborator'),'confirm_owner':routed.get('confirm_owner'),
              'reason':'; '.join(routed['reasons']) or None}]
    return {**routed,'recorded_by':'application','approval':'pending','status':'review_pending' if routed['reasons'] else 'proposed',
            'quote':f'quotes/{ident}.json' if quote.is_file() else None,'history':history}

DECISIONS={'approved':'approved','rejected':'rejected','revise_requested':'revise_requested','changed':'approved'}

def review(work,ident,decision,reason,by='PM',changes=None):
    path=work/'output/state'/f'{ident}.json'
    if not path.is_file():raise ValueError('먼저 state로 상태 기록을 만듭니다.')
    if decision not in DECISIONS:raise ValueError(f'결정은 {", ".join(DECISIONS)} 중 하나입니다.')
    if not reason or not reason.strip():raise ValueError('사람의 확인에는 이유가 필요합니다.')
    if decision=='changed' and not changes:raise ValueError('changed에는 --set 항목=값이 필요합니다.')
    current=read(path)
    if current['approval']!='pending':raise ValueError(f"이미 확인한 기록입니다: {current['approval']}. 다시 열려면 새 판으로 기록합니다.")
    last=current['history'][-1]
    entry={**{k:last.get(k) for k in ['category','role','collaborator','confirm_owner']},**(changes or {}),
           'version':last['version']+1,'actor':'human','by':by,'decision':decision,'reason':reason.strip(),
           'at':datetime.now().astimezone().isoformat(timespec='seconds')}
    entry['changed_fields']=[k for k in ['category','role','collaborator','confirm_owner'] if entry.get(k)!=last.get(k)]
    current['history'].append(entry)
    current.update({k:entry[k] for k in ['category','role','collaborator','confirm_owner']})
    current['approval']=DECISIONS[decision];current['status']=DECISIONS[decision]
    path.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return current

def review_cases(work,week,by='PM'):
    states=[read(p) for p in sorted((work/'output/state').glob('*.json'))]
    reviewed=[s for s in states if any(h['actor']=='human' for h in s['history'])]
    if not reviewed:raise ValueError('사람이 확인한 기록이 없습니다. review로 먼저 확인합니다.')
    changed=[s for s in reviewed if s['history'][-1].get('changed_fields')]
    same=[s for s in reviewed if not s['history'][-1].get('changed_fields')]
    text=f"---\nkind: review-cases\nweek: {week}\nconfirmed_by: {by}\nreviewed: {len(reviewed)}\nchanged: {len(changed)}\n---\n"
    for s in changed:
        h=s['history'][-1];prev=s['history'][-2]
        parts=[]
        for f in h['changed_fields']:
            label={'role':'담당 직군','category':'유형','collaborator':'협업 직군','confirm_owner':'확인 책임자'}[f]
            parts.append(f"{label} {prev.get(f) or '없음'} → {h.get(f)}")
        text+=f"- {s['inquiry_id']}: {'; '.join(parts)}. 이유: {h['reason']}\n"
    counts={}
    for s in same:counts[s.get('category') or '미정']=counts.get(s.get('category') or '미정',0)+1
    if same:text+=f"- 판정과 같았던 확인 {len(same)}건: "+', '.join(f'{k} {v}' for k,v in counts.items())+'.\n'
    text+='- 공통점(제안): 확인 필요 — PM이 사례를 읽고 적습니다.\n'
    target=work/'output/review-cases.md'
    if target.exists():raise ValueError('기존 확인 사례 원본을 보존합니다.')
    target.write_text(text,encoding='utf-8')
    return {'path':str(target),'reviewed':len(reviewed),'changed':len(changed),'note':'문의 원문·연락처는 넣지 않았습니다. 문의 ID로만 연결합니다.'}

def collect(work,version=None):
    rows=[]
    for row in read(work/'input/inquiries.json'):
        name=f"{row['id']}.{version}.json" if version else f"{row['id']}.json"
        path=work/'output/decisions'/name
        if not path.is_file():continue
        d=read(path);a=d.get('answers',{})
        routed=work/'output/routing'/name
        rows.append({'id':row['id'],'split':row['split'],'expected':row['expected'],
                     'predicted':{k:(a.get(k) or {}).get('choice') for k in ['category','role']},
                     'review_required':read(routed)['status']=='review_required' if routed.is_file() else None,
                     'data_origin':'measured' if d['_meta']['data_origin'].startswith('measured') else d['_meta']['data_origin'],
                     'provider':d['_meta']['provider']})
    if not rows:raise ValueError('판정 결과가 없습니다. decide를 먼저 실행합니다.')
    return rows

def record(work,command,status,elapsed,meta=None):
    meta=meta or {};usage=meta.get('usage') or {}
    row={'attempt_id':datetime.now().astimezone().isoformat(),'task_id':'part3-'+command,'status':status,
         'mode':'api' if meta.get('processing_location')=='cloud' else None,
         'processing_location':meta.get('processing_location'),'provider':meta.get('provider'),'model':meta.get('model_requested') or meta.get('model'),
         'elapsed_seconds':round(elapsed,3),'attempts':meta.get('attempts'),'input_tokens':usage.get('input_tokens'),'output_tokens':usage.get('output_tokens'),'cost_usd':None,
         'data_origin':'measured-runner','note':'실행기 경과시간. 모델·요금·콜드/웜 구분은 개별 응답과 대조합니다.'}
    with (work/'run-history.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['prepare','request','decide','decide-all','database','route','quote','state','review','review-cases','compare',
                                      'transcript-reference','extract','publish','confirm','wiki','mcp-config'])
    p.add_argument('task',nargs='?',help='wiki 명령의 위키 실습 ID(예: ch07-route-record)')
    p.add_argument('--workspace',type=Path,default=Path('work-part03'))
    p.add_argument('--inquiry',default='INQ-BB-D01-A')
    p.add_argument('--reference',action='store_true')
    p.add_argument('--transport',choices=['ollama','python','api'],default='ollama')
    p.add_argument('--engine',choices=['hermes','api'])
    p.add_argument('--version',help='질문·규칙의 새 판(예: v2). 결과는 <문의ID>.v2.json으로 따로 저장')
    p.add_argument('--criteria',type=Path,help='상용 판정에 함께 읽힐 판단 기준 페이지')
    p.add_argument('--predictions',type=Path)
    p.add_argument('--dev',action='store_true',help='compare: 개발 묶음 측정(평가 결과 아님)')
    p.add_argument('--decision',choices=list(DECISIONS))
    p.add_argument('--reason')
    p.add_argument('--by',default='PM')
    p.add_argument('--set',action='append',default=[],help='review: 항목=값 (role·category·collaborator·confirm_owner)')
    p.add_argument('--week',default='2026-10-12~2026-10-16')
    p.add_argument('--wiki-from',default='ch06')
    p.add_argument('--no-wiki',action='store_true')
    p.add_argument('--outputs',type=Path,help='wiki: 원본으로 쓸 결과 폴더(기본 <작업 폴더>/output)')
    a=p.parse_args();work=a.workspace.resolve();started=time.monotonic();meta=None
    try:
        if a.command=='prepare':prepare(work,a.wiki_from,not a.no_wiki);return
        unchanged(work)
        if a.command=='request':save(work/'output/laya-request.json',request_body(work,a.inquiry,a.version));result={'path':str(work/'output/laya-request.json')}
        elif a.command=='decide':result=decide(work,a.inquiry,a.reference,a.transport,a.version,a.criteria);meta=result['_meta']
        elif a.command=='decide-all':
            done=[]
            for row in read(work/'input/inquiries.json'):
                name=f"{row['id']}.{a.version}.json" if a.version else f"{row['id']}.json"
                if (work/'output/decisions'/name).exists():continue
                t0=time.monotonic()
                try:
                    d=decide(work,row['id'],a.reference,a.transport,a.version,a.criteria);routing(work,row['id'],a.version)
                    record(work,'decide',"ok",time.monotonic()-t0,d['_meta']);done.append(row['id'])
                except Exception as error:
                    record(work,'decide','failed',time.monotonic()-t0,dict(LAST_CALL) if LAST_CALL else {'processing_location':'cloud' if a.transport=='api' else 'local'})
                    LAST_CALL.clear()
                    print(f"{row['id']}: 확인 필요 — {error}",file=sys.stderr)
            result={'decided':len(done),'total':len(read(work/'input/inquiries.json'))}
        elif a.command=='database':result={'database':str(build_database(work))}
        elif a.command=='route':result=routing(work,a.inquiry,a.version)
        elif a.command=='quote':result=estimate(work,a.inquiry);save(work/'output/quotes'/f'{a.inquiry}.json',result)
        elif a.command=='state':
            result=state_record(work,a.inquiry);save(work/'output/state'/f'{a.inquiry}.json',result)
        elif a.command=='review':
            changes=dict(item.split('=',1) for item in a.set)
            result=review(work,a.inquiry,a.decision,a.reason,a.by,changes)
        elif a.command=='review-cases':result=review_cases(work,a.week,a.by)
        elif a.command=='compare':
            if a.dev:
                result=evaluation(collect(work,a.version),development=True)
                save(work/'output'/(f'comparison-dev.{a.version}.json' if a.version else 'comparison-dev.json'),result)
            else:
                if not a.predictions:raise ValueError('--predictions에 비교할 기록을 지정합니다. 내 판정 결과로 재려면 --dev를 씁니다.')
                result=evaluation(read(a.predictions),a.reference);save(work/'output/comparison.json',result)
        elif a.command=='transcript-reference':
            result=read(BASE/'ch09/completed/transcript.json');save(work/'output/transcript.json',result)
        elif a.command=='extract':result=extract_minutes(work,a.reference,a.engine);meta=result.get('_meta')
        elif a.command=='publish':result=publish_bundle(work)
        elif a.command=='confirm':result=confirm_bundle(work,a.by)
        elif a.command=='wiki':
            if a.task not in team_wiki.TASKS:raise ValueError('위키 실습 ID를 지정합니다: '+', '.join(team_wiki.TASKS))
            engine=a.engine or ('hermes' if shutil.which('hermes') else 'api')
            result=team_wiki.run(a.task,work/'wiki',(a.outputs.resolve() if a.outputs else work/'output'),engine,a.reference)
            save(work/'output/wiki-runs'/f'{a.task}.json',result)
            if not result['passed']:raise ValueError('위키 정리 검사 실패: '+'; '.join(result['problems']))
        else:
            uv=shutil.which('uv')
            if not uv:raise ValueError('uv 설치를 확인합니다.')
            cmd=['run','--no-project','--python','3.11','--with-requirements',str(BASE/'ch07/requirements-mcp.txt'),'python',str(BASE/'ch07/mcp_server.py'),'--database',str(work/'output/team.db')]
            print('mcp_servers:\n  studio_merry_readonly:\n    command: '+json.dumps(uv)+'\n    args: '+json.dumps(cmd,ensure_ascii=False));result={'configuration_printed':True}
        unchanged(work)
        if a.command!='decide-all':record(work,a.command,'ok',time.monotonic()-started,meta)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except Exception as error:
        if a.command in ('extract','decide') and LAST_CALL:meta=dict(LAST_CALL)
        if (work/'input-hashes.json').exists():record(work,a.command,'failed',time.monotonic()-started,meta)
        p.exit(1,f'확인 필요: {error}\n')

if __name__=='__main__':main()
