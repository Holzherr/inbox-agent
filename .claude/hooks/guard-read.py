#!/usr/bin/env python3
"""PreToolUse guard: only the email-reader subagent may fetch a thread.

get_thread is not in the allow list, so the main /email-triage agent - which
can label, draft and send - never sees an email body. Claude Code tags hook
input with agent_type when the call comes from a subagent; this hook approves
get_thread for email-reader and blocks it everywhere else.
"""
import json
import sys

READER = "email-reader"


def main():
    event = json.load(sys.stdin)
    if event.get("agent_type") == READER:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "email-reader reads thread bodies",
        }}))
        return
    print("guard-read: blocked - only the email-reader agent reads threads; hand it the thread id", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # fail closed
        print(f"guard-read: blocked - guard error: {e}", file=sys.stderr)
        sys.exit(2)
