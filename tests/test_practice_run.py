import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
sys.path.insert(0,str(BASE/"legacy"/"ch06"))
from scheduled_job import scheduled
spec=importlib.util.spec_from_file_location("practice_run",BASE/"run.py")
app=importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class WorkshopsTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work=Path(self.temp.name)/"책 실습 $()"
        with contextlib.redirect_stdout(io.StringIO()):
            app.prepare(self.work)

    def quiet_run(self,key,reference=False,**kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return app.run_task(app.TASKS[key],self.work,reference,**kwargs)

    def test_all_reference_packages_have_outputs_and_preserve_inputs(self):
        self.assertEqual(len(app.TASKS),33)
        for key,task in app.TASKS.items():
            if task.get("reference") is not False:
                self.quiet_run(key,True)
        history=[json.loads(s) for s in (self.work/"run-history.jsonl").read_text().splitlines()]
        self.assertTrue(all(r["mode"]=="reference" and r["cost_usd"] is None for r in history))

    def test_all_ready_local_operations(self):
        for key,task in app.TASKS.items():
            if task["operation"] not in ("model","wiki","costs-measured","drive-export"):
                self.quiet_run(key)
        report=(self.work/"output/weekly-report.md").read_text()
        self.assertIn("2.00%",report)
        self.assertIn("3.00%",report)
        self.assertIn("확인 필요",report)
        self.assertEqual(len(list((self.work/"output/brands").glob('*.md'))),3)

    def test_scheduled_job_gates_execution_and_preserves_same_day_success(self):
        with contextlib.redirect_stdout(io.StringIO()):
            closed=scheduled("ch06-morning-briefing",self.work,"2026-10-09T09:00:00+09:00",True,True)
            preview=scheduled("ch06-morning-briefing",self.work,"2026-10-08T09:00:00+09:00")
            first=scheduled("ch06-morning-briefing",self.work,"2026-10-08T09:00:00+09:00",True,True)
            second=scheduled("ch06-morning-briefing",self.work,"2026-10-08T09:01:00+09:00",True,True)
        self.assertFalse(closed["executed"])
        self.assertFalse(preview["executed"])
        self.assertTrue(first["executed"])
        self.assertFalse(second["executed"])
        self.assertEqual(len((Path(first["run_folder"])/"run-history.jsonl").read_text().splitlines()),1)

    def test_prepare_does_not_replace_existing_work(self):
        before=app.hashes(self.work)
        with self.assertRaises(ValueError): app.prepare(self.work)
        self.assertEqual(before,app.hashes(self.work))

    def test_existing_output_is_preserved(self):
        path=self.quiet_run("ch04-weekly-report")
        old=path.read_bytes()
        with self.assertRaises(ValueError): self.quiet_run("ch04-weekly-report")
        self.assertEqual(path.read_bytes(),old)

    def test_input_change_fails_before_execution(self):
        (self.work/"input/brief.md").write_text("변경")
        with self.assertRaises(ValueError): self.quiet_run("ch02-first-file",True)
        self.assertFalse((self.work/"output/first-file.md").exists())

    def test_unknown_client_goes_to_review_and_all_assets_are_copied(self):
        result=json.loads(self.quiet_run("ch03-organize").read_text())
        self.assertEqual(result["input_count"],result["classified_count"]+result["review_count"])
        self.assertEqual(result["review_count"],1)
        self.assertTrue((self.work/"output/organized/확인-필요/고객 미상.txt").exists())

    def test_rename_collision_fails_before_copying(self):
        path=self.work/"input/assets/manifest.json"
        rows=app.read_json(path)
        rows.append({**rows[0],"file":rows[1]["file"]})
        app.write_json(path,rows)
        with self.assertRaises(ValueError): app.organize(self.work,True)
        self.assertFalse((self.work/"output/renamed").exists())

    def test_paths_cannot_escape_workspace(self):
        with self.assertRaises(ValueError): app.inside(self.work,"../../outside.txt")

    def test_hours_convert_timezone_and_exclude_end_weekend_and_closed_date(self):
        config=app.read_json(self.work/"input/business-hours.json")
        self.assertTrue(app.business_time("2026-10-08T00:00:00+00:00",config)["within_business_hours"])
        for at in ["2026-10-08T18:00:00+09:00","2026-10-09T09:00:00+09:00","2026-10-10T10:00:00+09:00"]:
            self.assertFalse(app.business_time(at,config)["within_business_hours"])
        with self.assertRaises(ValueError): app.business_time("2026-10-08T09:00:00",config)

    def test_failed_and_retried_calls_are_both_charged_when_usage_known(self):
        records=[dict(attempt_id=str(i),task_id="x",status="failed" if i==1 else "ok",cost_usd="0.02",data_origin="measured") for i in (1,2)]
        result=app.cost_summary(records,{"checked_on":"test"})
        self.assertEqual(result["total_usd"],"0.04")
        self.assertEqual(result["failed_attempts"],1)

    def test_unknown_price_is_not_zero(self):
        result=json.loads(self.quiet_run("ch06-usage").read_text())
        self.assertIsNone(result["total_usd"])
        self.assertEqual(result["unpriced_attempts"],2)
        self.assertEqual(result["data_origin"],"synthetic")

    def test_latest_confirmed_event_drives_service_artifacts(self):
        result=json.loads(self.quiet_run("ch05-calendar").read_text())
        self.assertEqual(result["proposal"]["to"],"2026-10-15")
        self.assertEqual((result["proposal"]["action"],result["proposal"]["event_id"]),("update","CAL-BB-001"))
        self.assertEqual(result["not_changed"][0]["status"],"tentative")
        self.assertFalse(result["external_writes"])
        mail=json.loads(self.quiet_run("ch05-mail").read_text())
        self.assertEqual(mail["questions"],["최종 분량","검수 담당자"])
        self.assertNotIn("채널",mail["questions"])
        note=json.loads(self.quiet_run("ch05-notification").read_text())
        self.assertEqual(note["status"],"not_sent");self.assertIn("wiki/campaigns/",note["body"])

    def test_saved_prompt_is_passed_verbatim_as_file_to_ready_runner(self):
        # Stub exercises subprocess and output checks; it is not a live-model test.
        stub=Path(self.temp.name)/"stub-hermes"
        stub.write_text('#!/usr/bin/env python3\nimport sys,json\nfrom pathlib import Path\np=Path(sys.argv[-1])\ns=p.read_text()\nimport re\noutput=re.search(r"(/.*first-file\\.md)",s).group(1)\nPath(output).write_text("고객사: 봉봉소프트\\n확인된 조건\\n추가 질문: 확인 필요\\n")\nPath(output+".args").write_text(json.dumps(sys.argv[1:]))\n')
        stub.chmod(0o755)
        with patch.object(app.shutil,"which",return_value=str(stub)):
            target=self.quiet_run("ch02-first-file")
        argv=json.loads(Path(str(target)+".args").read_text())
        self.assertEqual(argv[:3],["chat","--oneshot","--query-file"])
        self.assertEqual(argv[3],str(self.work/"prompts/ch02-first-file.txt"))

    def fake_call(self,text,usage=(100,50)):
        return {"text":text,"provider":"gemini","model":"test-model","elapsed_seconds":0.1,"attempts":1,
                "usage":{"input_tokens":usage[0],"output_tokens":usage[1],"cache_read_tokens":None,"cache_write_tokens":None}}

    def test_api_engine_writes_result_and_records_usage_without_key(self):
        reply=self.fake_call("# 봉봉소프트 SNS 초안\n\n초안 문장\n\n## 확인 필요\n분량")
        with patch.object(app.llm,"complete",return_value=reply) as called:
            self.quiet_run("ch04-sns",engine="api")
        prompt=called.call_args[0][0]
        self.assertIn("product.md",prompt);self.assertIn("첨부 자료",prompt)
        row=[json.loads(s) for s in (self.work/"run-history.jsonl").read_text().splitlines()][-1]
        self.assertEqual((row["mode"],row["provider"],row["processing_location"],row["input_tokens"]),("api","gemini","cloud",100))
        summary=json.loads(self.quiet_run("ch06-usage-measured").read_text())
        self.assertEqual(summary["attempt_count"],1);self.assertIsNone(summary["total_usd"])
        self.assertEqual(summary["by_provider"]["gemini/test-model"]["output_tokens"],50)

    def test_forbidden_discontinued_feature_fails_check(self):
        reply=self.fake_call("# 봉봉소프트\n자동 견적 발송 기능\n확인 필요")
        with patch.object(app.llm,"complete",return_value=reply):
            with self.assertRaises(ValueError): self.quiet_run("ch04-sns",engine="api")

    def test_wiki_ingest_checks_sources_and_refuses_raw_writes(self):
        wiki=app.wiki_path(self.work)
        task=app.team_wiki.TASKS["ch03-wiki-ingest"]
        self.assertTrue(app.team_wiki.check(task,wiki))  # starter wiki is not organized yet
        written,refused=app.team_wiki.apply_files(wiki,[{"path":"raw/20261005_BB_brief.md","content":"x"},{"path":"../AGENTS.md","content":"x"}])
        self.assertEqual(written,[]);self.assertEqual(len(refused),2)
        page="---\ntype: client\n---\n- 확인 필요 (출처: raw/20261005_BB_brief.md)\n"
        research="- 요약 (출처: raw/20261006_TEAM_report-summary.md)\n"
        log=(wiki/"wiki/log.md").read_text()
        files=[{"path":"wiki/clients/BB.md","content":page},{"path":"wiki/research/report.md","content":research},
               {"path":"wiki/index.md","content":"- [BB](clients/BB.md)\n- [r](research/report.md)\n"},
               {"path":"wiki/log.md","content":log+"- 2026-10-05 정리 | 원본: raw/20261005_BB_brief.md\n- 2026-10-06 정리 | 원본: raw/20261006_TEAM_report-summary.md\n"}]
        replies=iter([self.fake_call(json.dumps({"files":files,"summary":"ok"})),self.fake_call(json.dumps({"files":[],"summary":"없음"}))])
        with patch.object(app.llm,"complete",side_effect=lambda *a,**k:next(replies)):
            self.quiet_run("ch03-wiki-ingest",engine="api")
        self.assertTrue((wiki/"raw/20261006_TEAM_report-summary.md").exists())

    def test_wiki_ingest_detects_rewritten_log(self):
        wiki=app.wiki_path(self.work)
        files=[{"path":"wiki/log.md","content":"# 새 기록\n- raw/20261005_BB_brief.md raw/20261006_TEAM_report-summary.md\n"}]
        with patch.object(app.llm,"complete",return_value=self.fake_call(json.dumps({"files":files}))):
            with self.assertRaises(ValueError): self.quiet_run("ch03-wiki-ingest",engine="api")
        record=json.loads((self.work/"output/wiki-runs/ch03-wiki-ingest.json").read_text())
        self.assertIn("log.md의 기존 기록이 바뀌었습니다(덧붙이기만 해야 함)",record["problems"])

    def test_wiki_call_is_recorded_even_when_response_json_is_broken(self):
        with patch.object(app.llm,"complete",return_value=self.fake_call("{not json")):
            with self.assertRaises(ValueError): self.quiet_run("ch03-wiki-ingest",engine="api")
        record=json.loads((self.work/"output/wiki-runs/ch03-wiki-ingest.json").read_text())
        self.assertEqual(record["calls"][0]["http"],"ok"); self.assertEqual(record["calls"][0]["content"],"failed")
        self.assertEqual(record["calls"][0]["usage"]["input_tokens"],100)

    def test_drive_export_is_one_way_split_by_client_and_tracks_removed_pages(self):
        with contextlib.redirect_stdout(io.StringIO()):
            app.run_task(app.TASKS["ch05-wiki-record"],self.work,True)
        result=json.loads(self.quiet_run("ch05-drive-export").read_text())
        folders={r["folder"] for r in result["rows"]}
        self.assertEqual(folders,{"팀 공유","BB 공유"})
        copy=(self.work/"output/drive-export"/result["rows"][0]["copy"]).read_text()
        self.assertTrue(copy.startswith("> 이 문서는 팀 위키의 읽기 전용 사본입니다."))
        self.assertFalse(any("raw/" in r["wiki_path"] for r in result["rows"]))
        old=self.work/"old-list.json"
        app.write_json(old,{"rows":[{"wiki_path":"wiki/clients/OLD.md","folder":"팀 공유","status":"갱신"}]})
        again=app.team_wiki.export(app.wiki_path(self.work),self.work/"export-2",previous=old)
        self.assertTrue(any(r["status"]=="삭제" and r["wiki_path"]=="wiki/clients/OLD.md" for r in again["rows"]))

    def test_provider_selection_and_json_parsing(self):
        with patch.dict(os.environ,{"GEMINI_API_KEY":"x","ANTHROPIC_API_KEY":"","OPENAI_API_KEY":"","TEAM_AGENT_PROVIDER":""}):
            self.assertEqual(app.llm.provider(),"gemini")
        with patch.dict(os.environ,{"TEAM_AGENT_PROVIDER":"claude","ANTHROPIC_API_KEY":""}):
            with self.assertRaises(app.llm.ModelError): app.llm.provider()
        self.assertEqual(app.llm.parse_json("```json\n{\"a\": 1}\n```"),{"a":1})
        self.assertEqual(app.llm.parse_json("앞 설명 {\"a\": 2} 끝"),{"a":2})
        self.assertEqual(app.llm.parse_json('{"a": "코드 \\u12 끝"}'),{"a":"코드 \\u12 끝"})  # 잘못된 \u 이스케이프 복구
        self.assertEqual(app.llm.parse_json('{"path":"C:\\\\users\\\\book","bad":"\\x","ok":"\\u0041\\n"}'),
                         {"path":"C:\\users\\book","bad":"\\x","ok":"A\n"})  # 정상 이스케이프는 그대로


if __name__=="__main__":
    unittest.main()
