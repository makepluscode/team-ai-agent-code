"""v1.7 actual local controls; no network model calls or synthetic success assertions."""
import hashlib
import json
import re
import sys

import pytest
from fastapi.testclient import TestClient

from team_work import requests as req
from team_work.workspace import PACKAGE_ROOT, prepare, verify


def start(tmp_path, chapter=11):
    work = tmp_path / f'ch{chapter}'
    prepare(chapter, work)
    req.init_workspace(work)
    return work


def test_intake_preserves_originals_and_duplicate_work(tmp_path):
    work = start(tmp_path, 7)
    req.intake(work, work/'input/internal-requests.json')
    data = req.intake(work, work/'input/optional-mail.json')
    assert len(data['requests']) == 10
    assert len(data['tasks']) == 11  # TASK-010 is only created by human review later.
    req.intake(work, work/'input/internal-requests.json')
    assert len(req.summary(work)['tasks']) == 11
    item = data['requests'][0]
    raw = work/item['original_file']
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == item['original_sha256']
    duplicate = dict(item, request_id='REQ-DUP', task_id='TASK-DUP')
    path=tmp_path/'duplicate.json';path.write_text(json.dumps([duplicate]))
    req.intake(work,path)
    result=req.summary(work)
    assert next(r for r in result['requests'] if r['request_id']=='REQ-DUP')['duplicate_of']==item['request_id']
    assert not any(t['task_id']=='TASK-DUP' for t in result['tasks'])
    verify(work)


def test_readonly_connection_cannot_change_database(tmp_path):
    work=start(tmp_path)
    import sqlite3
    with req.database(work,True) as db, pytest.raises(sqlite3.OperationalError):
        db.execute('DELETE FROM tasks')
    assert req.summary(work)['counts']=={'접수':0,'진행':2,'확인 대기':5,'수정 필요':0,'완료':5}


def test_classification_reference_and_failure_are_not_model_success(tmp_path, monkeypatch):
    work=start(tmp_path,8)
    result=req.classify(work,'REQ-001',work/'input/classification-reference/REQ-001.json')
    assert result['artifact_kind']=='author-reference'
    assert req.summary(work)['runs'][-1]['status']=='reference-read'
    def fail(*args,**kwargs):raise RuntimeError('secret key must never be logged')
    monkeypatch.setattr('team_work.models.call_commercial',fail)
    with pytest.raises(ValueError):req.classify(work,'REQ-007')
    result=req.summary(work)
    failed=next(r for r in result['runs'] if r['status']=='failed')
    assert failed['error']=='RuntimeError'
    assert 'secret' not in json.dumps(result)
    assert next(c for c in result['classifications'] if c['request_id']=='REQ-007')['needs_confirmation']
    assert not any(t['status']=='완료' for t in result['tasks'])


def test_model_call_uses_only_request_and_roles_and_records_actual_response(tmp_path, monkeypatch):
    work=start(tmp_path,8)
    def complete(system,prompt,**kwargs):
        payload=json.loads(prompt)
        assert set(payload)=={'request','roles','routing_criteria'}
        assert payload['routing_criteria']==req.read_json(work/'input/routing-criteria.json')
        assert 'owner_candidates' not in prompt
        value=req.read_json(work/'input/classification-reference/REQ-001.json')
        return {'text':json.dumps(value),'usage':{'input_tokens':12,'output_tokens':5},'provider':'mock-for-control-test'}
    monkeypatch.setattr('team_work.models.call_commercial',complete)
    result=req.classify(work,'REQ-001')
    assert result['artifact_kind']=='model-output'
    run=req.summary(work)['runs'][0]
    assert run['usage']['input_tokens']==12
    assert run['criteria_sha256']==hashlib.sha256((work/'input/routing-criteria.json').read_bytes()).hexdigest()


def test_reviews_six_preserve_correct_original_and_add_only_one_child(tmp_path):
    work=start(tmp_path,9)
    before=(work/'raw/DOC-009_r1.md').read_bytes()
    for i in range(1,7):req.review(work,work/f'input/reviews/REV-{i:03}.json','M05' if i==4 else 'M01',True)
    result=req.summary(work)
    assert len(result['reviews'])==6
    assert len(result['tasks'])==12
    assert (work/'raw/DOC-009_r1.md').read_bytes()==before
    assert '관측 완료4건' in (work/'output/DOC-009_r2.md').read_text()
    assert '10:00·회의실 A' in (work/'output/DOC-007_r3.md').read_text()
    assert (work/'output/DOC-013_r1.md').is_file()
    assert next(t for t in result['tasks'] if t['task_id']=='TASK-008')['children']==['TASK-009','TASK-010']
    for n in [1,2]:req.transition(work,f'TASK-{n:03}','완료','M01','사람이 수정 결과 확인',['raw/DOC-012_r1.md'],human=True)
    req.transition(work,'TASK-006','확인 대기','M04','슬라이드 수정 확인 요청',['raw/DOC-012_r1.md'])
    req.transition(work,'TASK-006','완료','M02','사람 확인',['raw/DOC-012_r1.md'],human=True)
    assert req.summary(work)['counts']=={'접수':0,'진행':2,'확인 대기':5,'수정 필요':0,'완료':5}


def test_review_rejects_wrong_link_and_cycle_and_preserves_transaction(tmp_path):
    work=start(tmp_path,9)
    item=req.read_json(work/'input/reviews/REV-003.json')
    item['task_id']='TASK-004'
    path=tmp_path/'wrong.json';path.write_text(json.dumps(item))
    with pytest.raises(ValueError,match='연결'):req.review(work,path,'M01',True)
    assert len(req.summary(work)['reviews'])==0
    assert len(req.summary(work)['tasks'])==11
    item['task_id']='TASK-008';item['children']=['TASK-008'];path.write_text(json.dumps(item))
    with pytest.raises(ValueError,match='순환'):req.review(work,path,'M01',True)
    assert len(req.summary(work)['tasks'])==11


def test_transition_requires_human_checks_stale_state_and_incomplete_children(tmp_path):
    work=start(tmp_path)
    with pytest.raises(ValueError):req.transition(work,'TASK-004','완료','M05','점수 높음',['ref'])
    req.transition(work,'TASK-008','확인 대기','M01','상태 검토',['ref'])
    with pytest.raises(ValueError,match='하위'):req.transition(work,'TASK-008','완료','M01','부모',['ref'],human=True)
    with pytest.raises(ValueError,match='바뀌'):req.transition(work,'TASK-004','수정 필요','M05','추가 확인',['ref'],expected='진행')
    assert req.summary(work)['counts']['완료']==5


def test_qa_twenty_historical_current_unknown_conflict_cancelled(tmp_path):
    work=start(tmp_path,10)
    assert req.qa_check(work)['ok']
    assert req.qa_check(work)['questions']==20
    assert '10/12' in req.qa_answer(work,'Q07')['answer']
    assert '미정' in req.qa_answer(work,'Q09')['answer']
    assert req.qa_answer(work,'Q16')['sources']==[]
    assert '충돌' in req.qa_answer(work,'Q17')['answer']
    assert '취소' in req.qa_answer(work,'Q19')['answer']
    assert '기각' in req.qa_answer(work,'Q20')['answer']
    (work/'raw/DOC-012_r1.md').unlink()
    with pytest.raises(ValueError):req.qa_answer(work,'Q01')


def test_dashboard_reads_same_counts_and_write_controls(tmp_path):
    work=start(tmp_path,12)
    client=TestClient(req.create_dashboard(work))
    assert client.get('/api/status').json()['counts']['완료']==5
    assert client.get('/api/briefing').json()['model_call'] is False
    assert 'sources' in client.get('/api/wiki-answer?query_id=Q01').json()
    assert client.post('/api/transition',json={}).status_code==403
    client=TestClient(req.create_dashboard(work,True))
    page=client.get('/').text
    assert '업무 지시' in page and 'REV-003' in page and 'TASK-009' in page
    assert '<form id="intake">' in page
    token=re.search("X-Team-Token':'([^']+)'",page)[1]
    item=req.read_json(work/'input/dashboard-request.json')[0]
    assert client.post('/api/intake',json=item,headers={'X-Team-Token':token}).status_code==200
    for state in ['진행','확인 대기','수정 필요','진행','확인 대기','완료']:
        current=next(t for t in req.summary(work)['tasks'] if t['task_id']=='TASK-013')['status']
        response=client.post('/api/transition',headers={'X-Team-Token':token},json={'task_id':'TASK-013','actor_id':'M01','status':state,'reason':'화면 사람 확인','source_ref':'input/dashboard-request.json#REQ-011','expected':current,'human_confirmed':True})
        assert response.status_code==200,response.text
    data=client.get('/api/status').json()
    assert len(data['requests'])==11 and len(data['tasks'])==13
    assert data['counts']['완료']==6 and data['counts']['확인 대기']==5
    assert client.post('/api/transition',json={}).status_code==403
    events=[e for e in data['events'] if e['target_refs']==['TASK-013']]
    assert len(events)==7 and all(e['data_kind']=='observed' for e in events)


def test_evaluation_split_and_gold_exclusion(tmp_path):
    root=PACKAGE_ROOT/'examples/requests/ch08'
    dev=req.read_json(root/'start/input/evaluation/development.json')
    evaluation=req.read_json(root/'start/input/evaluation/evaluation.json')
    assert len(dev)==18 and len(evaluation)==42
    assert not ({x['situation_id'] for x in dev}&{x['situation_id'] for x in evaluation})
    gold=req.read_json(root/'reference/evaluation-gold.json')
    assert len(gold)==60
    assert not any('owner_candidates' in x for x in dev+evaluation)
    predictions=tmp_path/'predictions.json';predictions.write_text(json.dumps(gold))
    result=req.evaluate(predictions,root/'reference/evaluation-gold.json')
    assert result['type_correct']==42 and result['owner_set_correct']==42
    assert result['model_quality_verified'] is False


@pytest.mark.asyncio
async def test_real_stdio_mcp_initialize_tools_list_call_and_no_write(tmp_path):
    from mcp.client.stdio import stdio_client

    from mcp import ClientSession, StdioServerParameters
    work=start(tmp_path,8)
    params=StdioServerParameters(command=sys.executable,args=['-m','team_work.cli','requests-mcp','--workspace',str(work)])
    before=hashlib.sha256(req.db_path(work).read_bytes()).hexdigest()
    async with stdio_client(params) as (read,write):  # noqa: SIM117 - session needs connected streams
        async with ClientSession(read,write,read_timeout_seconds=15) as session:
            await session.initialize()
            listed=await session.list_tools()
            assert {t.name for t in listed.tools}=={'get_request','get_roles'}
            result=await session.call_tool('get_request',{'request_id':'REQ-001'})
            assert not result.is_error
            assert 'REQ-001' in str(result.content)
            injection=await session.call_tool('get_request',{'request_id':"REQ-001' OR 1=1 --"})
            assert 'M02' not in str(injection.content)
            roles=await session.call_tool('get_roles',{})
            assert not roles.is_error and 'M05' in str(roles.content)
    assert hashlib.sha256(req.db_path(work).read_bytes()).hexdigest()==before


def test_all_chapter_snapshots_are_prior_events_and_references_are_consistent(tmp_path):
    from datetime import datetime
    for ch in range(7,13):
        work=start(tmp_path,ch)
        snap=req.read_json(work/'input/snapshot.json')
        assert all(datetime.fromisoformat(e['occurred_at'])<=datetime.fromisoformat(snap['as_of']) for e in snap['events'])
        ids={t['task_id'] for t in snap['tasks']}
        assert len(ids)==len(snap['tasks'])
        assert all(set(t['children'])<=ids for t in snap['tasks'])
        assert sum(t['task_id']=='TASK-009' for t in snap['tasks'])==1
        if ch>=10:
            assert len(snap['requests'])==10 and len(snap['tasks'])==12
    month=req.read_json(PACKAGE_ROOT/'examples/requests/ch12/reference/month-end-snapshot.json')
    assert len(month['requests'])==11 and len(month['tasks'])==13
    assert sum(t['status']=='완료' for t in month['tasks'])==6
    task9=next(t for t in month['tasks'] if t['task_id']=='TASK-009')
    assert task9['status']=='진행'


def test_all_public_reads_refuse_changed_originals(tmp_path):
    work=start(tmp_path)
    with (work/'raw/DOC-002_r1.md').open('a') as stream:stream.write('changed')
    with pytest.raises(ValueError,match='원본'):req.summary(work)
    with pytest.raises(ValueError,match='원본'):req.transition(work,'TASK-004','수정 필요','M05','확인',['ref'])
    with pytest.raises(ValueError,match='원본'):req.init_workspace(work)


def test_team_business_hours_overnight_briefing_owner_and_lock(tmp_path):
    from team_work import team_operations as ops
    work=start(tmp_path,12)
    for stamp,allowed in [('2026-10-19T08:59:59+09:00',False),('2026-10-19T09:00:00+09:00',True),
                          ('2026-10-19T17:59:59+09:00',True),('2026-10-19T18:00:00+09:00',False),
                          ('2026-10-17T10:00:00+09:00',False)]:
        assert ops.gate(work,stamp)['working_hours'] is allowed
    assert ops.gate(work,'2026-10-16T18:00:00+09:00')['next_open']=='2026-10-19T09:00:00+09:00'
    overnight={'request_id':'REQ-NIGHT','source_kind':'internal','requester_id':'M02',
               'received_at':'2026-10-16T19:00:00+09:00','body':'주말 사이 들어온 확인 요청',
               'source_ref':'provided:night-input','data_kind':'synthetic'}
    with req.database(work) as db:req._insert_request(db,overnight)
    brief=ops.briefing(work,'2026-10-19T09:00:00+09:00')
    assert brief['overnight_requests'][0]['request_id']=='REQ-NIGHT'
    assert [t['task_id'] for t in brief['overdue']]==['TASK-004','TASK-009']
    assert len(brief['pending'])==5
    ops.configure_owner(work,'M01')
    with pytest.raises(ValueError):ops.configure_owner(work,'M03')
    with ops.owner_lock(work,'M01'), pytest.raises(ValueError,match='중복'):
        ops.run_due(work,'M01','2026-10-19T09:00:00+09:00')
    skipped=ops.run_due(work,'M01','2026-10-19T18:00:00+09:00')
    assert skipped['run']['status']=='skipped-off-hours'
    result=ops.run_due(work,'M01','2026-10-19T09:00:00+09:00')
    assert result['run']['data_kind']=='synthetic'
    assert result['run']['usage'] is None and result['background_schedule_registered'] is False
    assert (work/result['run']['output_ref']).is_file()


@pytest.mark.parametrize("field,value", [("body",["not text"]),("requester_id","M99"),
    ("received_at","2026-10-13T10:00:00"),("due_at","2026-10-14T17:00:00"),
    ("source_kind","gmail"),("source_ref",None)])
def test_invalid_intake_batch_rolls_back_all_requests_and_tasks(tmp_path,field,value):
    work=start(tmp_path,7)
    original=req.read_json(work/'input/internal-requests.json')
    invalid=dict(original[1]);invalid[field]=value
    path=tmp_path/'invalid-batch.json';path.write_text(json.dumps([original[0],invalid]))
    with pytest.raises(ValueError):req.intake(work,path)
    data=req.summary(work)
    assert len(data['requests'])==0 and len(data['tasks'])==3


def test_team_run_failure_keeps_sanitized_run_and_releases_lock(tmp_path,monkeypatch):
    from team_work import team_operations as ops
    work=start(tmp_path,12);ops.configure_owner(work,'M01')
    def fail(*args,**kwargs):raise RuntimeError('secret failure body')
    monkeypatch.setattr(ops,'briefing',fail)
    with pytest.raises(ValueError,match='기록'):ops.run_due(work,'M01','2026-10-19T09:00:00+09:00')
    data=req.summary(work);run=data['runs'][-1]
    assert run['status']=='failed' and run['error']=='RuntimeError'
    assert 'secret' not in json.dumps(data) and run['event_id']
    assert not (work/'state/team-operation.lock').exists()


def test_early_briefing_does_not_include_future_overnight_request(tmp_path):
    from team_work import team_operations as ops
    work=start(tmp_path,12)
    item={'request_id':'REQ-LATER','source_kind':'internal','requester_id':'M02',
          'received_at':'2026-10-19T08:30:00+09:00','body':'아직 도착하지 않은 시각의 합성 요청',
          'source_ref':'provided:future','data_kind':'synthetic'}
    with req.database(work) as db:req._insert_request(db,item)
    assert not ops.briefing(work,'2026-10-19T08:00:00+09:00')['overnight_requests']


def test_dashboard_badges_filter_document_view_and_run_totals(tmp_path):
    work=start(tmp_path,12)
    client=TestClient(req.create_dashboard(work))
    page=client.get('/').text
    assert '편집 예시 판정' in page and '사람 ' in page
    filtered=client.get('/?owner=M05').text
    assert 'TASK-004' in filtered and 'TASK-006' not in filtered.split('<table>')[1].split('</table>')[0]
    doc=client.get('/doc',params={'path':'raw/DOC-012_r1.md#decision-01'})
    assert doc.status_code==200 and '읽기 전용' in doc.text
    assert client.get('/doc',params={'path':'../.exercise.json'}).status_code==404
    assert client.get('/doc',params={'path':'state/requests.sqlite3'}).status_code==404
    totals=req.run_totals([
        {'engine':'commercial','status':'succeeded','usage':{'input_tokens':10,'output_tokens':4},
         'started_at':'2026-10-18T01:00:00+00:00','finished_at':'2026-10-18T01:00:03+00:00','cost':None},
        {'engine':'commercial','status':'failed','usage':None,'started_at':None,'finished_at':None,'cost':None}])
    assert totals['commercial']=={'runs':2,'succeeded':1,'failed':1,'input_tokens':10,'output_tokens':4,'seconds':3.0,'cost':'미기록'}
