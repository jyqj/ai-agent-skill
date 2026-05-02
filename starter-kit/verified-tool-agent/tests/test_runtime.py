# Reference-only code for the ai-agent-architecture skill.
# Demonstrates architecture concepts or maintenance checks; not production-ready.
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_runtime import VerifiedToolAgent, task_from_dict


class VerifiedToolAgentTests(unittest.TestCase):
    def test_edit_and_verify(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / 'note.txt').write_text('hello world\n', encoding='utf-8')
            payload = {
                'goal': 'Replace hello with hi',
                'actions': [
                    {
                        'tool': 'edit_file',
                        'args': {'path': 'note.txt', 'old_text': 'hello', 'new_text': 'hi'},
                        'intended_effect': 'note.txt contains hi',
                        'verification': {'kind': 'contains', 'path': 'note.txt', 'value': 'hi'},
                    }
                ],
            }
            task = task_from_dict(payload)
            result = VerifiedToolAgent(workspace).run(task)
            self.assertTrue(result.success)
            self.assertIn('All actions verified', result.summary)
            self.assertIn('hi world', (workspace / 'note.txt').read_text(encoding='utf-8'))

    def test_failed_verification_stops(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / 'note.txt').write_text('hello world\n', encoding='utf-8')
            payload = {
                'goal': 'Cause verification failure',
                'actions': [
                    {
                        'tool': 'edit_file',
                        'args': {'path': 'note.txt', 'old_text': 'hello', 'new_text': 'hi'},
                        'intended_effect': 'note.txt contains bye',
                        'verification': {'kind': 'contains', 'path': 'note.txt', 'value': 'bye'},
                    },
                    {
                        'tool': 'edit_file',
                        'args': {'path': 'note.txt', 'old_text': 'hi', 'new_text': 'done'},
                        'intended_effect': 'should not run',
                        'verification': {'kind': 'contains', 'path': 'note.txt', 'value': 'done'},
                    },
                ],
            }
            task = task_from_dict(payload)
            result = VerifiedToolAgent(workspace).run(task)
            self.assertFalse(result.success)
            self.assertEqual(len(result.effects), 1)
            self.assertEqual(len(result.failures), 1)
            self.assertEqual(result.failures[0].category, 'effect_failed')
            self.assertIn('verification failed', result.summary)


    def test_tool_error_records_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            task = task_from_dict({
                'goal': 'Call missing tool',
                'actions': [
                    {
                        'tool': 'missing_tool',
                        'args': {},
                        'intended_effect': 'nothing happens',
                        'verification': {'kind': 'file_exists', 'path': 'x.txt'},
                    }
                ],
            })
            result = VerifiedToolAgent(Path(tmp)).run(task)
            self.assertFalse(result.success)
            self.assertEqual(result.failures[0].category, 'tool_error')
            self.assertIn('tool execution failed', result.summary)


if __name__ == '__main__':
    unittest.main()
