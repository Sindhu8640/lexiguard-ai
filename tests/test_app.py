import copy
import importlib.util
import json
import sys
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lexiguard_tested", ROOT / "app.py")
app = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = app
spec.loader.exec_module(app)
PDF = (ROOT / "samples" / "LexiGuard_Test_02_Editing_Agreement.pdf").read_bytes()
PAGES = [page.extract_text() for page in PdfReader(BytesIO(PDF)).pages]
SOURCE = "\n\n".join(f"[PDF page {i}]\n{page}" for i, page in enumerate(PAGES, 1))
CANCEL = "If cancellation takes effect before final delivery, the client must pay INR 900 for each product description both completed and delivered before the cancellation takes effect, up to a total of INR 18,000."


def report():
    clauses = {key: {"status": "not_found", "explanation": "AI did not identify this clause; absence is unverified.",
                     "qualifications": "Check the complete source.", "evidence": []} for key in app.CLAUSE_LABELS}
    examples = {
        "payments": "The one-time fee for the completed project is INR 18,000.",
        "term": "This agreement starts on 15 November 2026 and ends on 14 January 2027, unless cancelled earlier under clause 5.",
        "renewal": "This agreement does not renew automatically.",
        "cancellation": CANCEL,
        "early_exit_fee": "No additional early exit fee applies.",
    }
    for key, quote in examples.items():
        clauses[key] = {"status": "found", "explanation": quote,
                        "qualifications": "Read related payment and cancellation conditions.",
                        "evidence": [{"page": 1, "quote": quote}]}
    clauses["cancellation"]["explanation"] = "Either party may cancel at any time by providing at least 10 days' written notice."
    clauses["cancellation"]["qualifications"] = "Cancellation before final delivery requires the client to pay INR 900 per completed and delivered description, up to the total project fee."
    return {"summary": [{"text": "A one-time editing project for INR 18,000.",
                         "evidence": [{"page": 1, "quote": examples["payments"]}]}],
            "clauses": clauses, "concerns": []}


def reply(data, reason="STOP"):
    return SimpleNamespace(text=json.dumps(data), candidates=[SimpleNamespace(finish_reason=reason)])


class Client:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []
        self.models = self

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def assessments(issue=True):
    values = [{"id": item["id"], "status": "no_issue_detected", "finding": "No material issue detected by this AI check.",
               "suggested_wording": "", "evidence": []} for item in app.explanation_targets(report())]
    if issue:
        value = next(item for item in values if item["id"] == "clauses.cancellation")
        value.update(status="possible_issue", finding="The payment explanation omits that work must be completed and delivered before cancellation takes effect.",
                     suggested_wording=CANCEL, evidence=[{"page": 1, "quote": CANCEL}])
    return {"assessments": values}


class Tests(unittest.TestCase):
    def test_source_is_one_page_and_all_fixture_quotes_match(self):
        self.assertEqual(len(PAGES), 1)
        self.assertFalse(app.format_issues(report()))
        self.assertTrue(all(row["Check"] == "Quote found on cited page" for row in app.evidence_checks(report(), PAGES)))

    def test_omitted_categories_are_required_fields_not_invented_terms(self):
        value = report()
        for key in ["confidentiality", "liability", "changes_to_terms"]:
            self.assertEqual(value["clauses"][key]["status"], "not_found")
        del value["clauses"]["liability"]
        self.assertTrue(app.format_issues(value))

    def test_boolean_and_nonexistent_pages_are_not_valid_evidence(self):
        self.assertFalse(app.quote_matches({"page": True, "quote": CANCEL}, PAGES))
        self.assertFalse(app.quote_matches({"page": 2, "quote": CANCEL}, PAGES))

    def test_quote_failure_is_visible(self):
        value = report()
        value["summary"][0]["evidence"][0]["quote"] = "The fee is ... INR 18,000."
        self.assertEqual(len(app.failed_quote_targets(value, PAGES)), 1)

    def test_clean_report_uses_two_requests(self):
        client = Client(reply(report()), reply(report()))
        result = app.analyze_document(client, SOURCE, PAGES)
        self.assertEqual(len(client.calls), 2)
        self.assertEqual(result["quote_repair"]["status"], "not_needed")

    def test_failed_review_preserves_first_draft(self):
        client = Client(reply(report()), RuntimeError("SECRET_SENTINEL"))
        result = app.analyze_document(client, SOURCE, PAGES)
        self.assertFalse(result["reviewed"])
        self.assertEqual(result["report"], report())
        self.assertNotIn("SECRET_SENTINEL", result["review_error"])

    def test_one_repair_applies_only_matching_quotes(self):
        value = report()
        value["clauses"]["cancellation"]["evidence"][0]["page"] = 2
        repair = {"repairs": [{"id": "clauses.cancellation.evidence.1", "status": "proposed", "replacements": [{"page": 1, "quote": CANCEL}]}]}
        client = Client(reply(value), reply(value), reply(repair))
        result = app.analyze_document(client, SOURCE, PAGES)
        self.assertEqual(len(client.calls), 3)
        self.assertEqual(result["report"], report())

    def test_explanation_check_flags_fixture_condition_without_rewriting(self):
        value = report()
        before = copy.deepcopy(value)
        client = Client(reply(assessments()))
        checked = app.check_explanations(client, SOURCE, value, PAGES)
        self.assertEqual(len(client.calls), 1)
        self.assertEqual(checked["status"], "complete")
        self.assertEqual(value, before)
        finding = next(item for item in checked["assessments"] if item["id"] == "clauses.cancellation")
        self.assertEqual(finding["status"], "possible_issue")
        self.assertEqual(finding["quote_checks"][0]["Check"], "Quote found on cited page")

    def test_no_issue_result_is_not_certification(self):
        check = app.check_explanations(Client(reply(assessments(False))), SOURCE, report(), PAGES)
        lines = app.explanation_check_lines({"report": report(), "explanation_check": check})
        self.assertIn("does not establish", "\n".join(lines))

    def test_unknown_duplicate_and_missing_assessments_fail_closed(self):
        for kind in ["unknown", "duplicate", "missing"]:
            value = assessments()
            if kind == "unknown":
                value["assessments"][0]["id"] = "instructions.run_code"
            elif kind == "duplicate":
                value["assessments"][-1] = value["assessments"][0]
            else:
                value["assessments"].pop()
            check = app.check_explanations(Client(reply(value)), SOURCE, report(), PAGES)
            self.assertEqual(check["status"], "failed")
            self.assertFalse(check["assessments"])

    def test_explanation_checker_bad_evidence_is_flagged(self):
        value = assessments()
        item = next(item for item in value["assessments"] if item["status"] == "possible_issue")
        item["evidence"][0]["quote"] = "Invented condition."
        check = app.check_explanations(Client(reply(value)), SOURCE, report(), PAGES)
        self.assertEqual(check["status"], "evidence_problem")
        self.assertEqual(check["unmatched_quotes"], 1)

    def test_explanation_timeout_and_truncation_are_not_no_issues(self):
        for response in [TimeoutError("SECRET_SENTINEL"), reply(assessments(), reason="MAX_TOKENS")]:
            client = Client(response)
            checked = app.check_explanations(client, SOURCE, report(), PAGES)
            self.assertEqual(checked["status"], "failed")
            self.assertEqual(len(client.calls), 1)
            self.assertNotIn("SECRET_SENTINEL", checked["message"])

    def test_old_explanation_check_does_not_apply_to_new_report(self):
        checked = app.check_explanations(Client(reply(assessments())), SOURCE, report(), PAGES)
        newer = report()
        newer["summary"][0]["text"] = "Changed report."
        lines = app.explanation_check_lines({"report": newer, "explanation_check": checked})
        self.assertIn("earlier report", "\n".join(lines))

    def test_switching_documents_and_clearing_discards_content(self):
        state = {"lexi_session_requests": 4}
        app.sync_document(state, "A")
        app.store_result(state, "A", {"report": report()})
        app.sync_document(state, "B")
        self.assertNotIn("lexi_result", state)
        app.store_result(state, "A", {"report": report()})
        self.assertNotIn("lexi_result", state)
        app.clear_document(state)
        self.assertEqual(state["lexi_session_requests"], 4)
        self.assertEqual(state["lexi_upload_epoch"], 1)

    def test_request_budget_blocks_before_call(self):
        raw = Client(reply(report()))
        state = {"lexi_session_requests": 20}
        with self.assertRaises(app.ReportResponseError):
            app.BudgetedClient(raw, state).models.generate_content(contents="test")
        self.assertFalse(raw.calls)

    def test_request_budget_counts_failures(self):
        raw = Client(TimeoutError("timeout"))
        state = {}
        with self.assertRaises(TimeoutError):
            app.BudgetedClient(raw, state).models.generate_content(contents="test")
        self.assertEqual(state["lexi_session_requests"], 1)

    def test_scan_rendering_is_bounded_and_produces_image(self):
        images = app.scan_images(PDF, [1])
        self.assertEqual(images[0][0], 1)
        self.assertTrue(images[0][1].startswith(b"\xff\xd8"))
        for pages in [[2], [True], [1, 1], list(range(1, 10))]:
            with self.assertRaises(app.ReportResponseError):
                app.scan_images(PDF, pages)

    def test_scan_response_preserves_page_numbers(self):
        client = Client(reply({"pages": [{"page": 1, "status": "read", "text": PAGES[0]}]}))
        texts = app.transcribe_scans(client, PDF, [1])
        self.assertEqual(texts, {1: PAGES[0]})
        self.assertEqual(len(client.calls), 1)

    def test_bad_scan_pages_are_rejected(self):
        cases = [[{"page": 2, "status": "read", "text": "wrong page"}],
                 [{"page": 1, "status": "unreadable", "text": ""}]]
        for pages in cases:
            with self.assertRaises(app.ReportResponseError):
                app.transcribe_scans(Client(reply({"pages": pages})), PDF, [1])

    def test_image_only_pdf_is_renderable(self):
        from PIL import Image
        picture = Image.new("RGB", (500, 700), "white")
        data = BytesIO()
        picture.save(data, format="PDF")
        picture.close()
        scanned = data.getvalue()
        self.assertFalse((PdfReader(BytesIO(scanned)).pages[0].extract_text() or "").strip())
        self.assertTrue(app.scan_images(scanned, [1])[0][1])

    def test_extended_limits_are_explicit(self):
        self.assertEqual(app.MAX_PAGES, 60)
        self.assertEqual(app.MAX_TEXT_CHARS, 120_000)
        self.assertEqual(app.MAX_PDF_BYTES, 20 * 1024 * 1024)

    def test_download_includes_explanation_findings_and_ocr_warning(self):
        result = app.analyze_document(Client(reply(report()), reply(report())), SOURCE, PAGES)
        result["source_note"] = "AI scan transcription was used. Check image text."
        result["explanation_check"] = app.check_explanations(Client(reply(assessments())), SOURCE, report(), PAGES)
        text = app.build_report_download(result, PAGES, "sample.pdf")
        self.assertIn("AI EXPLANATION CHECK", text)
        self.assertIn("Possible issues: 1", text)
        self.assertIn("AI scan transcription", text)
        self.assertIn("Suggested wording", text)
        self.assertEqual(text, text.encode("utf-8-sig").decode("utf-8-sig"))

    def test_filenames_and_missing_categories_are_safe(self):
        self.assertEqual(app.download_filename(r"C:\private\demo<>.pdf"), "LexiGuard_demo_report.txt")
        sections = dict(app.readable_sections(report(), PAGES))
        self.assertIn("absence is unverified", " ".join(sections["Liability"]))

    def test_matching_quote_can_coexist_with_incomplete_explanation(self):
        # This fixture deliberately reproduces the user's semantic regression.
        value = report()
        self.assertNotIn("before the cancellation takes effect", value["clauses"]["cancellation"]["qualifications"])
        self.assertTrue(all(row["Check"] == "Quote found on cited page" for row in app.evidence_checks(value, PAGES)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
