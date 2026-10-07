# inbox-agent

An AI assistant for your inbox, built on Claude Code. It runs every hour on your Mac and:

- archives what doesn't need you, sorted into labels (finance, alerts, newsletters, notifications…)
- leaves the emails that need you in your inbox, with a reply drafted in your voice
- replies to cold growth-agency pitches with a counter-offer: you pay on an affiliate basis - 100% of the revenue from clients they bring you, up to a cap, then you share it
- sends you a 10-line digest on Slack every morning: who's waiting on you, money worth a look, pitches that said yes, newsletters worth unsubscribing from
- learns from your replies in the digest thread: "2 ignore", "unsub 3", "podcast invites should reach me", "drafts are too long"

Their AI cold-emails you. Your AI replies.

## What you need

- A Mac that stays on (a desktop, or a laptop that doesn't sleep). Linux works with cron instead of the scheduler below.
- A Claude Pro or Max plan, and [Claude Code](https://docs.claude.com/en/docs/claude-code) installed and logged in.
- Gmail, connected to Claude: claude.ai ▸ Settings ▸ Connectors ▸ Gmail.
- Slack for the digest (optional), connected the same way.

## Set up (about 30 minutes)

**1. Get the code**

```bash
git clone https://github.com/Holzherr/inbox-agent.git
cd inbox-agent
```

**2. Tell it about you**

Open `.claude/commands/email-triage.md` and fill in **About me**: your name, email, company, and Slack member ID. Change the reply text under **Cold pitches** if you want different wording.

Leave **Auto-send** at `no` for now. Replies are saved as Gmail drafts, so you can read what it would have sent.

**3. Dry run**

```bash
claude
```

Then type `/email-triage --dry-run`. It reads your inbox and prints what it would do, without changing anything. If something lands in the wrong bucket, tell it in plain English ("anything from stripe.com is finance") and ask it to add that to the rules.

**4. Real run**

Still in Claude, run `/email-triage`. Approve the permission prompts with "always allow" - the scheduled runs have no one to click yes. Then check Gmail: the new `Triage/` labels, the archived mail, and the drafted replies.

Then try the digest: `/email-triage --digest --slack`.

**5. Put it on a schedule**

```bash
./scheduler/install.sh
```

That's an hourly sweep 07:20–22:20 and the digest at 07:45. Change the times in `scheduler/*.plist` and re-run the installer. Run `./scheduler/install.sh --remove` to stop it.

On Linux, add this to `crontab -e` instead:

```
20 7-22 * * * /path/to/inbox-agent/scheduler/run.sh
45 7 * * *    /path/to/inbox-agent/scheduler/run.sh digest
```

**6. Turn on auto-send (when you trust it)**

After a few days of drafts that look right, set **Auto-send** to `yes`.

## How it behaves

- Emails can't give it orders. Only a reader agent with no email, Slack or web tools sees the email text; it returns a label, and the actions come from your rules. Emails that try to instruct an AI are flagged ⚠️ in the digest.
- It never deletes, trashes or marks spam. Archived mail is one search away.
- Replies to people who need you are drafts. It never sends them.
- When unsure, it leaves the email in your inbox.
- It replies to a pitch once per thread, at most 10 a day, never to anyone you've emailed before, and never to an auto-reply.
- Every action goes in `logs/actions.jsonl`, and every run in `logs/run.log`.
- Each scheduled run uses your Claude plan's usage, like any Claude Code session.

## Make it yours

The whole assistant is two files of plain English: `.claude/commands/email-triage.md` (what to do) and `.claude/agents/email-reader.md` (how to read an email and draft a reply). Most changes don't need either - tell it in the digest thread and it writes the rule itself.

## Troubleshooting

- **Nothing happens on schedule:** check `logs/run.log`. If it says `claude: command not found`, add the folder from `which claude` to `PATH` in `scheduler/run.sh`.
- **It stops at a permission prompt:** run it once by hand in `claude` and choose "always allow" for that tool.
- **"Not logged in" in the log:** the schedule has to run as you, logged into the Mac. Over SSH, Claude Code can't reach the login keychain.

Built by [Nick Holzherr](https://linkedin.com/in/nickholzherr). MIT licence.
