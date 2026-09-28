import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import provenance as p


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def event(self, text=" 我自己的想法。\n保留空白。 ", revision="1", **overrides):
        source = self.root / ("source-" + revision + ".json")
        source.write_text(json.dumps({"role": "user", "content": text}, ensure_ascii=True), encoding="utf-8")
        event = {"id": "dsh:session:message:" + hashlib.sha256(text.encode()).hexdigest(),
                 "kind": "dsh", "session_id": "session", "message_id": "message",
                 "source_path": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                 "source_line": 1, "timestamp": "2026-09-22T12:00:00+08:00", "verbatim": text,
                 "course": "示例", "lesson": "01"}
        return {**event, **overrides}

    def test_capture_duplicate_is_byte_identical_and_preserves_verbatim(self):
        event = self.event()
        first = p.capture(self.root, event)
        ledger = (self.root / p.LEDGER).read_bytes()
        atoms = (self.root / p.ATOMS).read_bytes()
        second = p.capture(self.root, event)
        self.assertEqual(first, second)
        self.assertEqual(ledger, (self.root / p.LEDGER).read_bytes())
        self.assertEqual(atoms, (self.root / p.ATOMS).read_bytes())
        self.assertEqual(first["verbatim"], event["verbatim"])
        self.assertFalse(first["claim_eligible"])
        self.assertEqual(first["semantic_origin"], "unknown")

    def test_same_message_revision_adds_record_and_reused_id_is_rejected(self):
        event = self.event()
        first = p.capture(self.root, event)
        revised = self.event("修改后的真实用户话", "2")
        with self.assertRaisesRegex(ValueError, "新 ID"):
            p.capture(self.root, {**revised, "id": event["id"]})
        second = p.capture(self.root, revised)
        self.assertNotEqual(first["record_id"], second["record_id"])
        self.assertEqual(len(p._rows(self.root / p.LEDGER)), 2)
        self.assertEqual(p.get_record(self.root, event["id"])["verbatim"], event["verbatim"])

    def test_mixed_cannot_upgrade_to_user_and_keeps_original_ledger(self):
        event = self.event("书中说甲。我认为乙。")
        p.capture(self.root, event)
        before = (self.root / p.LEDGER).read_bytes()
        spans = [{"text": "书中说甲。", "origin": "material", "source_ref": "book:1"},
                 {"text": "我认为乙。", "origin": "user"}]
        with self.assertRaises(ValueError):
            p.set_attribution(self.root, event["id"], "user", "错误整体升级", spans)
        reviewed = p.set_attribution(self.root, event["id"], "mixed", "材料引用与自己的判断混合", spans)
        self.assertEqual(reviewed["requested_origin"], "mixed")
        self.assertEqual(reviewed["semantic_origin"], "unknown")
        self.assertFalse(reviewed["strict_mastery_evidence_allowed"])
        with self.assertRaises(ValueError):
            p.set_attribution(self.root, event["id"], "user", "省略已有材料切片")
        self.assertEqual(before, (self.root / p.LEDGER).read_bytes())
        atom = p.to_atom(p._lookup(self.root, event["id"]), self.root)
        self.assertFalse(atom["learning"]["is_feynman_evidence"])
        self.assertFalse(atom["eligibility"]["as_user_claim"])
        self.assertEqual(atom["voice_policy"]["first_person"], "forbidden")

    def test_user_review_is_not_gateway_authentication(self):
        event = self.event()
        p.capture(self.root, event)
        result = p.set_attribution(self.root, event["id"], "user", "人工判断候选")
        self.assertEqual(result["requested_origin"], "user")
        self.assertEqual(result["semantic_origin"], "unknown")
        self.assertNotIn("attribution_id", result)
        self.assertFalse(result["claim_eligible"])

    def test_source_hash_change_is_rejected(self):
        event = self.event()
        p.capture(self.root, event)
        Path(event["source_path"]).write_text("篡改来源", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            p.get_record(self.root, event["id"])
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            p.set_attribution(self.root, event["id"], "user", "不能跨版本复用")

    def test_review_hash_change_is_rejected(self):
        event = self.event()
        p.capture(self.root, event)
        p.set_attribution(self.root, event["id"], "unknown", "待核对")
        path = self.root / p.REVIEWS
        review = p._rows(path)[0]
        review["origin"] = "user"
        path.write_text(json.dumps(review), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            p.get_record(self.root, event["id"])

    def test_verbatim_hash_change_is_rejected(self):
        event = self.event()
        p.capture(self.root, event)
        record = p._rows(self.root / p.LEDGER)[0]
        record["verbatim"] = "篡改原话"
        (self.root / p.LEDGER).write_text(json.dumps(record), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "原话 SHA-256"):
            p.get_record(self.root, event["id"])

    def test_snapshot_keeps_original_message_after_live_source_changes(self):
        event = self.event()
        snapshot = self.root / "immutable-source.json"
        snapshot.write_bytes(Path(event["source_path"]).read_bytes())
        p.capture(self.root, {**event, "source_snapshot_path": str(snapshot)})
        Path(event["source_path"]).write_text("新版本", encoding="utf-8")
        self.assertEqual(p.get_record(self.root, event["id"])["verbatim"], event["verbatim"])

    def test_unrelated_atom_bytes_preserved(self):
        atom_path = self.root / p.ATOMS
        atom_path.parent.mkdir(parents=True)
        original = b'{ "evidence_id" : "ev_unrelated", "arbitrary": true }\n'
        atom_path.write_bytes(original)
        p.capture(self.root, self.event())
        self.assertTrue(atom_path.read_bytes().startswith(original))
        backups = list((self.root / ".trash").glob("*_evidence-atoms.jsonl_*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)

    def test_multiple_text_blocks_join_exactly_from_source_snapshot(self):
        event = self.event(" 第一段 \n第二段\n尾行")
        snapshot = self.root / "source-snapshot.json"
        snapshot.write_text(json.dumps({"message": {"role": "user", "content": [
            {"type": "text", "text": " 第一段 "},
            {"type": "image", "data": "not-text"},
            {"type": "text", "text": "第二段\n尾行"}]}}), encoding="utf-8")
        event.update(source_snapshot_path=str(snapshot), source_line=512,
                     source_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest())
        result = p.capture(self.root, event)
        self.assertEqual(result["verbatim"], " 第一段 \n第二段\n尾行")
        with self.assertRaisesRegex(ValueError, "逐字内容"):
            p.capture(self.root, {**event, "verbatim": "第一段\n第二段\n尾行"})

    def test_plain_note_snapshot_uses_snapshot_start_not_live_source_line(self):
        event = self.event("逐字笔记\n不改格式", kind="note")
        snapshot = self.root / "note.txt"
        snapshot.write_text(event["verbatim"], encoding="utf-8")
        event.update(source_snapshot_path=str(snapshot), source_line=99,
                     source_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest())
        self.assertEqual(p.capture(self.root, event)["verbatim"], event["verbatim"])

    def test_jsonl_line_locator_and_ambiguous_spans(self):
        event = self.event("重复重复")
        path = Path(event["source_path"])
        path.write_text('{"content":"前文"}\n' + json.dumps({"content": event["verbatim"]}) + "\n")
        event.update(source_line=2, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        p.capture(self.root, event)
        with self.assertRaisesRegex(ValueError, "重复子串"):
            p.set_attribution(self.root, event["id"], "unknown", "复核", [{"text": "重复", "origin": "user"}])


if __name__ == "__main__":
    unittest.main()
