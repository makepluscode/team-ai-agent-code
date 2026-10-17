import contextlib
import importlib.util
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
spec=importlib.util.spec_from_file_location('part3',BASE/'part3.py')
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)

class Part03Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        with contextlib.redirect_stdout(io.StringIO()):self.work=app.prepare(Path(self.tmp.name)/'책 실습 $()',with_wiki=False)
        self.ident='INQ-BB-D01-A'
    def test_independent_package_and_no_answer_labels_in_model_input(self):
        data=app.read(self.work/'input/inquiries.json');self.assertEqual(len(data),30)
        self.assertEqual(len({r['situation_id'] for r in data}),10)
        self.assertTrue(all(r['split']=='development-preview' for r in data))
        self.assertTrue(all('expected' not in r for r in app.read(self.work/'model-input/inquiries.json')))
        self.assertNotIn('expected',json.dumps(app.request_body(self.work,self.ident)))
        self.assertFalse((self.work/'model-input/comparison-structure.json').exists())
    def test_prepare_preserves_existing_and_hashes_detect_changes(self):
        with self.assertRaises(ValueError):app.prepare(self.work)
        (self.work/'input/questions.json').write_text('{}')
        with self.assertRaises(ValueError):app.unchanged(self.work)
    def test_readonly_database_rejects_update_and_does_not_contain_labels(self):
        db=app.build_database(self.work)
        with app.readonly(db) as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM inquiries').fetchone()[0],30)
            self.assertEqual(len(con.execute('PRAGMA table_info(inquiries)').fetchall()),3)
            with self.assertRaises(sqlite3.OperationalError):con.execute("UPDATE customers SET name='wrong'")
    def test_reference_decision_and_routing_are_simulation_and_not_assignment(self):
        app.decide(self.work,self.ident,True);r=app.routing(self.work,self.ident)
        self.assertTrue(r['simulation']);self.assertEqual(r['status'],'review_required')
        self.assertIsNone(r['person_assigned']);self.assertFalse(r['external_assignment'])
    def test_missing_confidence_and_refusal_route_to_review(self):
        d=app.decide(self.work,'INQ-BB-D03-A',True)
        d['answers']['role']={'type':'refusal'};d['answers']['category']['confidence']=None
        path=self.work/'output/decisions/INQ-BB-D03-A.json';path.write_text(json.dumps(d))
        r=app.routing(self.work,'INQ-BB-D03-A');self.assertEqual(r['status'],'review_required');self.assertIsNone(r['role'])
    def test_invalid_choice_and_nonfinite_score_do_not_auto_assign(self):
        d=app.decide(self.work,'INQ-BB-D03-A',True)
        d['answers']['role']['choice']='영업';d['answers']['urgency']['score']=float('nan')
        (self.work/'output/decisions/INQ-BB-D03-A.json').write_text(json.dumps(d))
        r=app.routing(self.work,'INQ-BB-D03-A');self.assertEqual(r['status'],'review_required')
    def test_same_type_has_independent_roles(self):
        a=app.decide(self.work,self.ident,True);b=app.decide(self.work,'INQ-BB-D06-A',True)
        self.assertEqual(a['answers']['category']['choice'],b['answers']['category']['choice'])
        self.assertNotEqual(a['answers']['role']['choice'],b['answers']['role']['choice'])
    def test_exact_quote_with_tax_and_no_send_permission(self):
        app.build_database(self.work);r=app.estimate(self.work,self.ident)
        self.assertEqual((r['supply_krw'],r['tax_krw'],r['total_krw']),(400000,40000,440000))
        self.assertFalse(r['send_allowed']);self.assertEqual(r['status'],'review_required')
    def test_unknown_sku_and_missing_quantity_have_no_amount(self):
        app.build_database(self.work)
        for ident in ['INQ-LB-D09-A','INQ-DP-D08-A']:
            r=app.estimate(self.work,ident);self.assertIsNone(r['total_krw']);self.assertEqual(r['status'],'review_required')
    def test_preview_data_cannot_be_reported_as_measured_accuracy(self):
        row={'id':'x','expected':{'category':'견적','role':'기획'},'predicted':{'category':'견적','role':'기획'},'split':'development-preview','data_origin':'authored-fixture'}
        with self.assertRaises(ValueError):app.evaluation([row])
        self.assertIsNone(app.evaluation([row],True)['accuracy'])
        with self.assertRaises(ValueError):app.evaluation([row,row],True)
    def test_reference_minutes_keep_tentative_cancelled_unknown_and_pending_publication(self):
        app.save(self.work/'output/transcript.json',app.read(BASE/'ch09/completed/transcript.json'))
        r=app.extract_minutes(self.work,True);self.assertEqual(r['actions'][1]['due'],None)
        self.assertTrue(any(d['status']=='tentative' for d in r['decisions']));self.assertTrue(r['cancelled'])
        publication=app.publish_bundle(self.work);self.assertFalse(publication['external_writes']);self.assertFalse(publication['wiki_built'])
        self.assertIn('publication_pending',(self.work/'output/wiki-input/meeting.md').read_text())
        with self.assertRaises(ValueError):app.publish_bundle(self.work)
    def test_foreign_meeting_and_missing_evidence_rejected(self):
        r=app.read(BASE/'ch09/completed/minutes.json');r['meeting_id']='OTHER'
        with self.assertRaises(ValueError):app.validate_minutes(r,app.read(self.work/'input/meeting.json'))
        r['meeting_id']='MEET-BB-1008';r['decisions'][0]['evidence']=''
        with self.assertRaises(ValueError):app.validate_minutes(r,app.read(self.work/'input/meeting.json'))
    def test_existing_decision_is_preserved(self):
        app.decide(self.work,self.ident,True)
        with self.assertRaises(ValueError):app.decide(self.work,self.ident,True)
    def fake(self,answers):
        return {'text':json.dumps(answers,ensure_ascii=False),'provider':'gemini','model':'test-model','elapsed_seconds':0.1,'attempts':1,
                'usage':{'input_tokens':300,'output_tokens':40,'cache_read_tokens':None,'cache_write_tokens':None}}
    def test_commercial_decision_has_same_format_and_is_not_simulation(self):
        reply=self.fake({'category':{'choice':'견적','confidence':0.95},'role':{'choice':'기획','confidence':0.9},'urgency':{'score':0},'contract_stop':{'noul':0.0},'evidence':'견적을 요청'})
        with patch.object(app.llm,'complete',return_value=reply) as called:
            d=app.decide(self.work,self.ident,transport='api')
        self.assertNotIn('expected',called.call_args[0][0])
        self.assertEqual((d['_meta']['processing_location'],d['_meta']['data_origin'],d['_meta']['provider']),('cloud','measured-cloud','gemini'))
        self.assertEqual(d['answers']['role'],{'type':'choice','choice':'기획','confidence':0.9,'probabilities':None})
        r=app.routing(self.work,self.ident);self.assertFalse(r['simulation']);self.assertEqual(r['processing_location'],'cloud')
        self.assertIn('일정·견적 조건 확인',r['reasons'])
    def test_commercial_decision_parse_failure_keeps_call_record(self):
        with patch.object(app.llm,'complete',return_value=self.fake('x') | {'text':'not json'}):
            with self.assertRaises(Exception):app.decide(self.work,self.ident,transport='api')
        self.assertEqual(app.LAST_CALL['usage']['input_tokens'],300)

    def test_http_failure_does_not_reuse_previous_call_record(self):
        with patch.object(app.llm,'complete',return_value=self.fake({'category':{'choice':'견적','confidence':0.9},'role':{'choice':'기획','confidence':0.9},'urgency':{'score':0},'contract_stop':{'noul':0}})):
            app.decide(self.work,self.ident,transport='api')
        err=app.llm.ModelError('상용 API 오류 503',503);err.provider,err.model,err.attempts='gemini','m',5
        with patch.object(app.llm,'complete',side_effect=err):
            with self.assertRaises(app.llm.ModelError):app.decide(self.work,'INQ-BB-D06-A',transport='api')
        self.assertEqual((app.LAST_CALL['usage'],app.LAST_CALL['attempts'],app.LAST_CALL['http']),(None,5,'failed'))

    def test_v2_questions_add_collaborator_and_applied_criteria_rule(self):
        reply=self.fake({'category':{'choice':'견적','confidence':0.95},'role':{'choice':'개발','confidence':0.9},'collaborator':{'choice':'기획','confidence':0.8},'urgency':{'score':0},'contract_stop':{'noul':0.0}})
        with patch.object(app.llm,'complete',return_value=reply):
            d=app.decide(self.work,'INQ-BB-D06-A',transport='api',version='v2')
        self.assertEqual(d['_meta']['questions_version'],2)
        r=app.routing(self.work,'INQ-BB-D06-A','v2');self.assertEqual(r['collaborator'],'기획');self.assertIn('협업 직군 기획 확인',r['reasons'])
        self.assertTrue((self.work/'output/routing/INQ-BB-D06-A.v2.json').exists())
        app.decide(self.work,'INQ-LB-D09-A',True)
        before=app.routing(self.work,'INQ-LB-D09-A');self.assertIsNone(before['confirm_owner'])
        app.decide(self.work,'INQ-LB-D09-A',True,version='v2');after=app.routing(self.work,'INQ-LB-D09-A','v2')
        self.assertEqual((after['confirm_owner'],after['role']),('PM','기획'));self.assertEqual(after['criteria_applied'],['CRIT-OFFLIST-PM'])
    def test_multi_item_quote_is_high_amount(self):
        app.build_database(self.work);r=app.estimate(self.work,'INQ-BB-D06-C')
        self.assertEqual((r['supply_krw'],r['tax_krw'],r['total_krw']),(1400000,140000,1540000));self.assertEqual(r['reason'],'고액 금액 확인')
        self.assertEqual(len(r['lines']),2)
    def test_review_requires_reason_keeps_history_and_feeds_review_cases(self):
        for ident in [self.ident,'INQ-BB-D06-A','INQ-LB-D09-A']:
            app.decide(self.work,ident,True);app.routing(self.work,ident);app.save(self.work/'output/state'/f'{ident}.json',app.state_record(self.work,ident))
        with self.assertRaises(ValueError):app.review(self.work,self.ident,'approved','  ')
        app.review(self.work,self.ident,'approved','단가표와 일치')
        with self.assertRaises(ValueError):app.review(self.work,self.ident,'approved','두 번')
        r=app.review(self.work,'INQ-BB-D06-A','changed','캠페인 메시지가 새로 들어간다',changes={'collaborator':'기획'})
        self.assertEqual([h['version'] for h in r['history']],[1,2]);self.assertEqual(r['history'][1]['changed_fields'],['collaborator'])
        app.review(self.work,'INQ-LB-D09-A','changed','단가표 밖 협업',changes={'confirm_owner':'PM'})
        out=app.review_cases(self.work,'2026-10-12~2026-10-16')
        self.assertEqual((out['reviewed'],out['changed']),(3,2))
        text=(self.work/'output/review-cases.md').read_text()
        self.assertIn('확인 책임자 없음 → PM',text);self.assertIn('판정과 같았던 확인 1건',text)
        body=app.inquiry(self.work,self.ident)['body'];self.assertNotIn(body,text)
    def test_publish_writes_raw_named_files_with_all_lists_and_redaction(self):
        t=app.read(BASE/'ch09/completed/transcript.json');t['segments'].append({'start':12.0,'end':18.5,'text':'연락은 pm@studiomerry.example 또는 010-1234-5678로 주세요.'})
        app.save(self.work/'output/transcript.json',t);app.extract_minutes(self.work,True)
        out=app.publish_bundle(self.work);self.assertEqual(out['redactions'],2);self.assertEqual(out['evidence_missing_after_redaction'],[])
        meeting=(self.work/'output/wiki-input/20261008_BB_CAMP-BB-202610_meeting.md').read_text()
        for word in ['## 취소','금요일 다음 회의안','## 할 일','기한: 확인 필요','## 미정 조건','CTA 주소','status: publication_pending']:self.assertIn(word,meeting)
        tr=(self.work/'output/wiki-input/20261008_BB_CAMP-BB-202610_transcript.md').read_text()
        self.assertNotIn('pm@studiomerry.example',tr);self.assertIn('[00:12~00:18]',tr)
        app.confirm_bundle(self.work,'PM');self.assertIn('status: confirmed',(self.work/'output/wiki-input/20261008_BB_CAMP-BB-202610_meeting.md').read_text())
        with self.assertRaises(ValueError):app.confirm_bundle(self.work,'PM')
    def test_development_measurement_is_not_reported_as_accuracy(self):
        rows=[{'id':'a','expected':{'category':'견적','role':'기획'},'predicted':{'category':'견적','role':'개발'},'data_origin':'measured','review_required':True}]
        r=app.evaluation(rows,development=True);self.assertIsNone(r['accuracy']);self.assertEqual(r['development_accuracy'],{'category':1.0,'role':0.0})
        with self.assertRaises(ValueError):app.evaluation([{**rows[0],'data_origin':'authored-fixture'}],development=True)
    def test_publish_rejects_evidence_missing_from_transcript(self):
        app.save(self.work/'output/transcript.json',app.read(BASE/'ch09/completed/transcript.json'))
        r=app.read(BASE/'ch09/completed/minutes.json');r['decisions'][0]['evidence']='회의에서 나오지 않은 문장'
        app.save(self.work/'output/minutes.json',r)
        with self.assertRaises(ValueError):app.publish_bundle(self.work)

    def test_grouped_decisions_are_flattened_with_status(self):
        r=app.normalize_minutes({'decisions':{'confirmed':[{'id':'D1','value':'발행일 2026-10-15','evidence':'변경됐습니다'}],'cancelled':[{'id':'D2','value':'금요일 회의','evidence':'취소합니다'}]}})
        self.assertEqual([(d['id'],d['status']) for d in r['decisions']],[('D1','confirmed'),('D2','cancelled')])

if __name__=='__main__':unittest.main()
