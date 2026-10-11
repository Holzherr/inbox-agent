#!/usr/bin/env python3
"""PreToolUse guard for the only two ways this agent can send mail.

The model reading this inbox can be talked into things by an email. This hook
can't: it lets a send through only when it matches what the command allows.

- reply: plain text, to the thread's sender only, body exactly the affiliate
  template in .claude/commands/email-triage.md.
- send_message: an empty "unsubscribe" email to one address, nothing else.

Exit 2 blocks the tool call and shows the reason to the model.
"""
import json
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMMAND = os.path.join(ROOT, ".claude", "commands", "email-triage.md")


def template():
    text = open(COMMAND, encoding="utf-8").read()
    section = text.split("## Cold pitches", 1)[1]
    m = re.search(r"```\n(.*?)```", section, re.S)
    return m.group(1)


def norm(s):
    return "\n".join(line.rstrip() for line in (s or "").strip().splitlines())


def deny(reason):
    print(f"guard-send: blocked - {reason}", file=sys.stderr)
    sys.exit(2)


def main():
    event = json.load(sys.stdin)
    tool = event.get("tool_name", "")
    args = event.get("tool_input") or {}

    if tool.endswith("Gmail__reply"):
        for field in ("to", "cc", "bcc", "htmlBody"):
            if args.get(field):
                deny(f"reply may not set {field}")
        if args.get("replyAll"):
            deny("reply-all is not allowed")
        if norm(args.get("body")) != norm(template()):
            deny("reply body must be exactly the affiliate template; save anything else as a draft")
        return

    if tool.endswith("Gmail__send_message"):
        for field in ("cc", "bcc", "htmlBody", "attachments", "draftId", "replyThreadId", "replyToMessageId"):
            if args.get(field):
                deny(f"send_message may not set {field}")
        to = args.get("to") or []
        if len(to) != 1:
            deny("send_message must have exactly one recipient")
        if (args.get("subject") or "").strip().lower() != "unsubscribe" or norm(args.get("body")):
            deny("send_message is only for empty 'unsubscribe' emails")
        return


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # fail closed: an error must not let a send through
        deny(f"guard error: {e}")
