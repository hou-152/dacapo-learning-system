"""文件行为回归；合成来源与假模型只验证流程，不代表真实模型验收。"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import backend
import provenance


class BackendBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / '真源'
        self.root.mkdir()
        (self.root / 'SOURCE_OF_TRUTH.md').write_text('# 测试真源\n')
        skill = self.root / '09-Skills/dbs-learning/SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_text('按真实反馈继续；原文保持逐字。')
        self.original = '# 第一篇\n\n正文解释因果与条件。\n\n## 学习反馈\n\n> 旧手写反馈不能删除。\n'
        for course in ('甲课', '乙课'):
            folder = self.root / '02-课程真源' / course
            folder.mkdir(parents=True)
            (folder / '01.md').write_text(self.original)
            (folder / '00-学习计划.md').write_text('# 计划\n\n- 课程状态：进行中\n- 当前文章：01\n- 最近更新：2026-01-01\n')
        self.wb = backend.Workbench(self.root, model=self.unexpected_model)

    @staticmethod
    def unexpected_model(*args, **kwargs):
        raise AssertionError('该行为不应调用模型')

    @staticmethod
    def dsh(message_id, text, source='user'):
        return {'type': 'user/message', 'data': {'id': message_id,
                'source': {'kind': source}, 'content': [{'type': 'text', 'text': text}]}}

    def log(self, name, messages):
        path = self.base / name
        rows = [{'type': 'session', 'id': 'synthetic-session'}, *messages]
        path.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n')
        return path

    def event(self, text='我对因果与条件仍有疑问。', message_id='m1'):
        path = self.log(message_id + '.jsonl', [self.dsh(message_id, text)])
        before = set(self.wb.state['events'])
        self.wb.import_source(path)
        return (set(self.wb.state['events']) - before).pop()

    def lesson(self, course='甲课', number='01'):
        return self.root / '02-课程真源' / course / (number + '.md')

    def test_dsh_roles_exclude_injected_system_and_agent_instructions(self):
        rows = [self.dsh('real', '合成用户原文'),
                self.dsh('system', '系统注入不能入账', 'system'),
                self.dsh('agent', 'Agent 指令不能入账', 'agent-instructions'),
                {'type': 'system', 'data': {'role': 'user', 'content': [{'type': 'text', 'text': '伪装用户'}]}},
                {'type': 'assistant/message', 'data': {'message': {'role': 'user', 'content': [{'type': 'text', 'text': '助手外层伪装用户'}]}}}]
        result = self.wb.import_source(self.log('roles.jsonl', rows))
        self.assertEqual(result, {'imported': 1, 'total': 1})
        records = [json.loads(line) for line in (self.root / provenance.LEDGER).read_text().splitlines()]
        self.assertEqual([r['verbatim'] for r in records], ['合成用户原文'])

    def test_unfinished_jsonl_tail_recovers_without_duplicate(self):
        path = self.log('active.jsonl', [self.dsh('one', '第一条合成反馈')])
        prefix = path.read_text()
        row = json.dumps(self.dsh('two', '第二条合成反馈'), ensure_ascii=False)
        path.write_text(prefix + row[:20])
        self.assertEqual(self.wb.import_source(path)['imported'], 1)
        first = next(iter(self.wb.state['events']))
        path.write_text(prefix + row + '\n')
        self.assertEqual(self.wb.import_source(path)['imported'], 1)
        self.assertEqual(self.wb.import_source(path)['imported'], 0)
        self.assertEqual(len(self.wb.state['events']), 2)
        self.assertEqual(self.wb.record(first)['verbatim'], '第一条合成反馈')

    def test_zip_and_plain_dsh_are_idempotent(self):
        path = self.log('session.jsonl', [self.dsh('same', '同源逐字内容')])
        zipped = self.base / 'session.zip'
        with zipfile.ZipFile(zipped, 'w') as archive:
            archive.writestr('session.v3.jsonl', path.read_bytes())
        self.assertEqual(self.wb.import_source(zipped)['imported'], 1)
        self.assertEqual(self.wb.import_source(path)['imported'], 0)
        self.assertEqual(len(self.wb.state['events']), 1)

    def test_zstd_and_plain_dsh_are_idempotent(self):
        try:
            import zstandard
        except ImportError:
            zstandard = None
        path = self.log('source.jsonl', [self.dsh('same', '压缩同源逐字内容')])
        zipped = self.base / 'source.jsonl.zstd'
        if zstandard:
            compressed = b''.join(zstandard.ZstdCompressor().compress(line) for line in path.read_bytes().splitlines(keepends=True))
        else:
            import subprocess
            compressed = subprocess.run([str(Path.home() / '.npm-global/bin/node'), '-e',
                'const z=require("node:zlib");let a=[];process.stdin.on("data",x=>a.push(x));process.stdin.on("end",()=>{for(const s of Buffer.concat(a).toString().split(/(?<=\\n)/))if(s)process.stdout.write(z.zstdCompressSync(Buffer.from(s)));});'],
                input=path.read_bytes(), capture_output=True, check=True).stdout
        zipped.write_bytes(compressed)
        self.assertEqual(self.wb.import_source(zipped)['imported'], 1)
        self.assertEqual(self.wb.import_source(path)['imported'], 0)

    def test_pi_source_id_survives_copy_and_reimport(self):
        path = self.log('pi.jsonl', [
            {'type': 'message', 'id': 'pi-user', 'message': {'role': 'user', 'content': [{'type': 'text', 'text': 'Pi 合成反馈'}]}},
            {'type': 'message', 'id': 'pi-system', 'message': {'role': 'system', 'content': [{'type': 'text', 'text': '排除系统'}]}}])
        self.assertEqual(self.wb.import_source(path)['imported'], 1)
        copy = self.base / 'pi-copy.jsonl'
        copy.write_bytes(path.read_bytes())
        self.assertEqual(self.wb.import_source(copy)['imported'], 0)
        self.assertEqual(len(self.wb.state['events']), 1)

    def test_note_revision_preserves_both_originals(self):
        self.wb.inbox.mkdir(parents=True)
        note = self.wb.inbox / '反馈.md'
        first_text = '第一版  原文\n保留标点！\n'
        note.write_text(first_text)
        self.wb.import_source(note)
        first = next(iter(self.wb.state['events']))
        note.write_text('第二版独立原文。\n')
        self.wb.import_source(note)
        self.assertEqual(len(self.wb.state['events']), 2)
        self.assertEqual(self.wb.record(first)['verbatim'], first_text)
        self.assertEqual(self.wb.import_source(note)['imported'], 0)

    def test_scan_catches_dsh_pi_and_inbox_added_while_closed(self):
        from unittest.mock import patch
        home = self.base / 'home'
        dsh = home / '.dsh/sessions/--Users-housibo-Documents-~4EA4~4E92~5F0F~5B66~4E60--'
        pi = home / '.pi/agent/sessions/--Users-housibo-Documents-交互式学习--'
        dsh.mkdir(parents=True)
        pi.mkdir(parents=True)
        log = dsh / 'live.jsonl'
        log.write_text(json.dumps({'type': 'session', 'id': 'restart-dsh'}) + '\n')
        with patch.object(backend.Path, 'home', return_value=home):
            self.wb.scan()
            with log.open('a') as out:
                out.write(json.dumps(self.dsh('new', '关闭期间的 DSH 合成反馈')) + '\n')
            (pi / 'new.jsonl').write_text(json.dumps({'type': 'session', 'id': 'restart-pi'}) + '\n' + json.dumps(
                {'type': 'message', 'id': 'new', 'message': {'role': 'user', 'content': [{'type': 'text', 'text': '关闭期间的 Pi 合成反馈'}]}}) + '\n')
            (self.wb.inbox / 'new.txt').write_text('关闭期间的合成笔记')
            restarted = backend.Workbench(self.root, model=self.unexpected_model)
            self.assertEqual(restarted.scan()['imported'], 3)
            self.assertEqual(restarted.scan()['imported'], 0)
            self.assertEqual({v['kind'] for v in restarted.state['events'].values()}, {'dsh', 'pi', 'note'})

    def test_assign_appends_preserves_old_and_is_idempotent(self):
        event_id = self.event('新增反馈逐字！\n  缩进也属于原文。')
        self.wb.assign(event_id, '甲课', '01', 'user')
        first = self.lesson().read_text()
        self.assertTrue(first.startswith(self.original))
        self.assertIn('> 新增反馈逐字！\n>   缩进也属于原文。', first)
        self.wb.assign(event_id, '甲课', '01', 'user')
        self.assertEqual(self.lesson().read_text(), first)
        self.assertEqual(first.count(f'<!-- WB_FEEDBACK id={event_id} -->'), 1)

    def test_cross_course_reassignment_moves_only_owned_block(self):
        moved = self.event('这条应改归另一课程。', 'move')
        kept = self.event('这条留在原课程。', 'keep')
        self.wb.assign(moved, '甲课', '01', 'user')
        self.wb.assign(kept, '甲课', '01', 'user')
        self.wb.assign(moved, '乙课', '01', 'user')
        old = self.lesson().read_text()
        new = self.lesson('乙课').read_text()
        self.assertTrue(old.startswith(self.original))
        self.assertIn(f'<!-- WB_FEEDBACK id={kept} -->', old)
        self.assertNotIn(f'<!-- WB_FEEDBACK id={moved} -->', old)
        self.assertIn(f'<!-- WB_FEEDBACK id={moved} -->', new)
        self.assertIn('这条应改归另一课程。', new)
        atom = provenance.to_atom(self.wb.record(moved), self.root)
        self.assertEqual(atom['learning']['course'], '乙课')
        self.assertEqual(atom['learning']['lesson'], '01')
        self.assertFalse(atom['eligibility']['as_user_claim'])

    def test_ambiguous_short_message_does_not_follow_model_guess(self):
        event_id = self.event('再展开一下')
        self.wb.model = lambda *a, **k: json.dumps({'kind': 'feedback', 'origin': 'user', 'course': '甲课', 'lesson': '01', 'reason': '模型猜测'})
        self.wb.classify(event_id)
        self.assertEqual(self.wb.state['events'][event_id]['status'], 'review')
        self.assertEqual(self.lesson().read_text(), self.original)

    def test_model_failure_keeps_queue_and_verbatim_after_restart(self):
        event_id = self.event()
        def fail(*a, **k):
            raise RuntimeError('合成模型连接失败')
        self.wb.model = fail
        result = self.wb.process()
        self.assertTrue(result['errors'])
        restarted = backend.Workbench(self.root, model=fail)
        self.assertEqual(restarted.state['events'][event_id]['status'], 'model_error')
        self.assertEqual(restarted.record(event_id)['verbatim'], '我对因果与条件仍有疑问。')
        self.assertEqual(self.lesson().read_text(), self.original)

    def test_canvas_preserves_user_layout_nodes_and_connections(self):
        self.wb.canvas('甲课')
        path = self.lesson().parent / '学习画布.canvas'
        value = json.loads(path.read_text())
        value['nodes'][0].update(x=321, y=-999, color='4', width=678)
        value['nodes'].append({'id': 'user-note', 'type': 'text', 'text': '我的批注', 'x': 6, 'y': 9, 'width': 200, 'height': 100})
        value['edges'].append({'id': 'user-edge', 'fromNode': 'user-note', 'toNode': value['nodes'][0]['id'], 'label': '自定义'})
        path.write_text(json.dumps(value, ensure_ascii=False))
        self.wb.assign(self.event(), '甲课', '01', 'user')
        updated = json.loads(path.read_text())
        for node in value['nodes']:
            if node['id'].startswith('lw-status-'):
                continue  # 状态卡由工具按实测数字刷新，不属于用户布局
            self.assertIn(node, updated['nodes'])
        self.assertIn(value['edges'][0], updated['edges'])
        again = path.read_bytes()
        self.wb.canvas('甲课')
        self.assertEqual(path.read_bytes(), again)

    def test_canvas_cross_course_reassignment_removes_stale_owned_node(self):
        event_id = self.event()
        self.wb.assign(event_id, '甲课', '01', 'user')
        view = self.wb.state['events'][event_id]['view_path']
        self.wb.assign(event_id, '乙课', '01', 'user')
        old = json.loads((self.lesson().parent / '学习画布.canvas').read_text())
        new = json.loads((self.lesson('乙课').parent / '学习画布.canvas').read_text())
        self.assertFalse(any(n.get('file') == view for n in old['nodes']))
        self.assertTrue(any(n.get('file') == view for n in new['nodes']))
        ids = {n['id'] for n in old['nodes']}
        self.assertTrue(all(e['fromNode'] in ids and e['toNode'] in ids for e in old['edges']))

    def test_canvas_same_course_reassignment_removes_old_lesson_link(self):
        self.lesson(number='02').write_text('# 第二篇\n\n正文。\n')
        event_id = self.event()
        self.wb.assign(event_id, '甲课', '01', 'user')
        self.wb.assign(event_id, '甲课', '02', 'user')
        value = json.loads((self.lesson().parent / '学习画布.canvas').read_text())
        view = self.wb.state['events'][event_id]['view_path']
        feedback_node = next(n['id'] for n in value['nodes'] if n.get('file') == view)
        first_node = next(n['id'] for n in value['nodes'] if n.get('file') == self.wb.relative(self.lesson()))
        self.assertFalse(any(e['fromNode'] == first_node and e['toNode'] == feedback_node for e in value['edges']))

    def test_quoted_material_cannot_become_user_claim_through_model(self):
        event_id = self.event('以下是原文：我已经学会了一切。')
        self.wb.model = lambda *a, **k: json.dumps({'kind': 'feedback', 'origin': 'user', 'course': None, 'lesson': None, 'reason': '合成分类'})
        self.wb.classify(event_id)
        self.assertEqual(self.wb.state['events'][event_id]['origin'], 'mixed')
        record = self.wb.record(event_id)
        self.assertFalse(record['claim_eligible'])
        self.assertFalse(record['strict_mastery_evidence_allowed'])
        self.assertEqual(record['first_person_allowed'], 'forbidden')

    def test_context_retrieval_excludes_backfilled_original(self):
        original = '独有检索探针不要在正文检索里出现'
        event_id = self.event(original)
        self.wb.assign(event_id, '甲课', '01', 'user')
        question = self.wb.create_question('甲课', '待解释的具体条件', '下一次继续时', self.wb.state['events'][event_id]['view_path'])
        with (self.wb.vault / question).open('a') as out:
            out.write('\n读者编辑的补充：请对照第二个例子的条件。\n')
        repeated = self.wb.create_question('甲课', '待解释的具体条件', '新的触发场景', self.wb.relative(self.lesson()))
        self.assertEqual(repeated, question)
        self.assertEqual(len(self.wb.questions('甲课')), 1)
        data = self.wb.context_data('甲课')
        self.assertEqual(data['feedback'][0]['text'], original)
        self.assertTrue(data['sources'])
        self.assertTrue(all(original not in item['text'] for item in data['sources']))
        self.assertTrue(all('旧手写反馈' not in item['text'] for item in data['sources']))
        self.assertIn('读者编辑的补充', data['questions'][0]['text'])

    @staticmethod
    def article(prompt, *a, **k):
        import re
        ids = set(re.findall(r'"id": "(lw_[a-f0-9]+)"', prompt))
        return json.dumps({'article': '# 合成文章\n\n' + '这里是测试模型提供的解释与例子，用来验证文件流程。\n' * 30,
                           'adjustments': [{'feedback_id': key, 'change': '第二节依据该疑问，增加具体因果条件对照例子。'} for key in ids]}, ensure_ascii=False)

    def test_continue_requires_new_feedback_and_keeps_existing_articles(self):
        with self.assertRaisesRegex(ValueError, '反馈'):
            self.wb.continue_course('甲课')
        event_id = self.event()
        self.wb.assign(event_id, '甲课', '01', 'user')
        old = self.lesson().read_bytes()
        self.wb.model = self.article
        result = self.wb.continue_course('甲课')
        self.assertTrue(result['path'].endswith('/02.md'))
        self.assertEqual(self.lesson().read_bytes(), old)
        self.assertIn(event_id, self.lesson(number='02').read_text())
        with self.assertRaisesRegex(ValueError, '新反馈'):
            self.wb.continue_course('甲课')
        self.assertFalse(self.lesson(number='03').exists())

    def test_continue_rejects_completed_course(self):
        self.wb.assign(self.event(), '甲课', '01', 'user')
        plan = self.lesson().parent / '00-学习计划.md'
        plan.write_text(plan.read_text().replace('进行中', '已结课'))
        with self.assertRaisesRegex(ValueError, '结课'):
            self.wb.continue_course('甲课')
        self.assertFalse(self.lesson(number='02').exists())

    def test_continue_does_not_overwrite_concurrent_next_article(self):
        self.wb.assign(self.event(), '甲课', '01', 'user')
        target = self.lesson(number='02')
        def competing_writer(*a, **k):
            target.write_text('# 另一写入者已保存的正文\n')
            return self.article(*a, **k)
        self.wb.model = competing_writer
        with self.assertRaises((backend.Conflict, ValueError)):
            self.wb.continue_course('甲课')
        self.assertEqual(target.read_text(), '# 另一写入者已保存的正文\n')
        self.assertNotIn('甲课', self.wb.state['next_runs'])

    def test_continue_recovers_after_article_written_before_plan_update(self):
        self.wb.assign(self.event(), '甲课', '01', 'user')
        self.wb.model = self.article
        original_write = self.wb.write
        def fail_plan(path, text, **kwargs):
            if Path(path).name == '00-学习计划.md':
                raise backend.Conflict('合成并行编辑')
            original_write(path, text, **kwargs)
        self.wb.write = fail_plan
        with self.assertRaises(backend.Conflict):
            self.wb.continue_course('甲课')
        created = self.lesson(number='02').read_bytes()
        restarted = backend.Workbench(self.root, model=self.unexpected_model)
        result = restarted.continue_course('甲课')
        self.assertTrue(result['path'].endswith('/02.md'))
        self.assertEqual(self.lesson(number='02').read_bytes(), created)
        self.assertFalse(self.lesson(number='03').exists())
        self.assertIn('当前文章：02', (self.lesson().parent / '00-学习计划.md').read_text())

    def test_canvas_links_questions_and_candidates_to_source(self):
        key = self.event()
        self.wb.assign(key, '甲课', '01', 'user')
        source = self.wb.state['events'][key]['view_path']
        question = self.wb.create_question('甲课', '因果如何区分？', '遇到相关不等于因果的例子', source)
        candidate = self.wb.save_candidate(key, 'QST', {'title': '因果问题', 'idea': '对照条件'})['path']
        canvas = json.loads((self.lesson().parent / '学习画布.canvas').read_text())
        ids = {n['file']: n['id'] for n in canvas['nodes'] if 'file' in n}
        for path in (question, candidate):
            self.assertTrue(any(e['fromNode'] == ids[source] and e['toNode'] == ids[path] for e in canvas['edges']))

    def test_canvas_renders_status_card_above_content(self):
        key = self.event()
        self.wb.assign(key, '甲课', '01', 'user')
        canvas = json.loads((self.lesson().parent / '学习画布.canvas').read_text())
        card = next(n for n in canvas['nodes'] if n['id'].startswith('lw-status-'))
        self.assertEqual(card['type'], 'text')
        status = self.wb.loop_status('甲课')
        self.assertIn(f"正文 {status['lessons']} 篇", card['text'])
        self.assertIn(f"入账 {status['banked_feedback']}", card['text'])
        self.assertIn(f"已结清 {status['resolved_questions']}", card['text'])
        for node in canvas['nodes']:
            if 'file' in node:
                self.assertLessEqual(card['y'] + card['height'], node['y'])

    def test_path_traversal_and_outside_inbox_are_rejected(self):
        with self.assertRaises(ValueError):
            self.wb.course_path('../02-课程真源')
        with self.assertRaises(ValueError):
            self.wb.lesson_path('甲课', '../01')
        with self.assertRaises(ValueError):
            self.wb.write(self.base / 'outside.md', '越界')
        outside = self.base / 'outside-note.md'
        outside.write_text('不可收取收件箱外笔记')
        with self.assertRaises(ValueError):
            self.wb.import_source(outside)
        self.assertEqual(self.wb.state['events'], {})


if __name__ == '__main__':
    unittest.main()
