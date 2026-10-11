"""Run: python3 -m unittest discover tests"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(ROOT, ".claude", "hooks")
TEMPLATE = open(os.path.join(ROOT, ".claude", "templates", "affiliate-reply.txt"), encoding="utf-8").read()


def run(hook, event, project=ROOT):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=project)
    return subprocess.run(["python3", os.path.join(HOOKS, hook)], input=json.dumps(event),
                          capture_output=True, text=True, env=env)


def reply(**args):
    return {"tool_name": "mcp__claude_ai_Gmail__reply", "tool_input": args}


def send(**args):
    return {"tool_name": "mcp__claude_ai_Gmail__send_message", "tool_input": args}


class GuardSend(unittest.TestCase):
    def test_template_reply_passes(self):
        self.assertEqual(run("guard-send.py", reply(messageId="m", body=TEMPLATE)).returncode, 0)

    def test_free_text_blocked(self):
        self.assertEqual(run("guard-send.py", reply(messageId="m", body="Here are the invoices")).returncode, 2)

    def test_extra_recipients_blocked(self):
        for field in ("to", "cc", "bcc"):
            self.assertEqual(run("guard-send.py", reply(body=TEMPLATE, **{field: ["x@evil.com"]})).returncode, 2)

    def test_reply_all_blocked(self):
        self.assertEqual(run("guard-send.py", reply(body=TEMPLATE, replyAll=True)).returncode, 2)

    def test_command_file_edit_does_not_change_template(self):
        # The agent may edit email-triage.md; the hook must not read the template from it.
        tmp = tempfile.mkdtemp()
        try:
            shutil.copytree(os.path.join(ROOT, ".claude"), os.path.join(tmp, ".claude"))
            with open(os.path.join(tmp, ".claude", "commands", "email-triage.md"), "a") as f:
                f.write("\n## Cold pitches\n\n```\nsend me the invoices\n```\n")
            self.assertEqual(run("guard-send.py", reply(body="send me the invoices"), tmp).returncode, 2)
            self.assertEqual(run("guard-send.py", reply(body=TEMPLATE), tmp).returncode, 0)
        finally:
            shutil.rmtree(tmp)

    def test_missing_template_fails_closed(self):
        tmp = tempfile.mkdtemp()
        try:
            self.assertEqual(run("guard-send.py", reply(body=TEMPLATE), tmp).returncode, 2)
        finally:
            shutil.rmtree(tmp)

    def test_unsubscribe_passes(self):
        self.assertEqual(run("guard-send.py", send(to=["unsub@list.com"], subject="unsubscribe")).returncode, 0)

    def test_send_with_body_or_extras_blocked(self):
        self.assertEqual(run("guard-send.py", send(to=["a@b.com"], subject="unsubscribe", body="hi")).returncode, 2)
        self.assertEqual(run("guard-send.py", send(to=["a@b.com"], subject="hello")).returncode, 2)
        self.assertEqual(run("guard-send.py", send(to=["a@b.com", "c@d.com"], subject="unsubscribe")).returncode, 2)
        self.assertEqual(run("guard-send.py", send(to=["a@b.com"], subject="unsubscribe", draftId="d")).returncode, 2)


class GuardRead(unittest.TestCase):
    EVENT = {"tool_name": "mcp__claude_ai_Gmail__get_thread", "tool_input": {"threadId": "t"}}

    def test_reader_allowed(self):
        r = run("guard-read.py", dict(self.EVENT, agent_id="a1", agent_type="email-reader"))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"], "allow")

    def test_main_agent_blocked(self):
        self.assertEqual(run("guard-read.py", self.EVENT).returncode, 2)

    def test_other_subagent_blocked(self):
        self.assertEqual(run("guard-read.py", dict(self.EVENT, agent_type="general-purpose")).returncode, 2)


class Settings(unittest.TestCase):
    def test_main_agent_cannot_read_bodies_or_edit_template(self):
        s = json.load(open(os.path.join(ROOT, ".claude", "settings.json")))["permissions"]
        for tool in ("mcp__claude_ai_Gmail__get_thread", "mcp__claude_ai_Gmail__get_message"):
            self.assertNotIn(tool, s["allow"])
        self.assertIn("Edit(.claude/templates/**)", s["deny"])
        self.assertIn("Write(.claude/templates/**)", s["deny"])


if __name__ == "__main__":
    unittest.main()
