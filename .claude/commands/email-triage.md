---
description: Triage my inbox — answer cold growth pitches with an affiliate offer, label + archive noise, and (with --digest) send me what needs me
---

Keeps my inbox down to the mail that needs me. Uses the Gmail and Slack connectors (`mcp__claude_ai_Gmail__*`, `mcp__claude_ai_Slack__*`). Runs hourly from `scheduler/run.sh`; `--digest` runs once a day.

## About me — edit this

- **Name:** YOUR NAME
- **Email:** you@yourcompany.com
- **Company:** YOUR COMPANY — one line on what it does
- **Slack member ID for the digest:** U00000000 (Slack ▸ your profile ▸ ⋯ ▸ Copy member ID)
- **Auto-send pitch replies:** no — `no` saves each reply as a Gmail draft for me to send; `yes` sends it.
- **Max pitch replies per day:** 10

## Flags

- *(none)* — sweep only.
- `--digest` — sweep, then write the daily digest.
- `--slack` — DM the digest to me. Without it, print it.
- `--dry-run` — classify and print what would happen. No sends, drafts, label changes or log writes.

## Labels

Use these Gmail labels, all under `Triage/`: `Cold pitch`, `Finance`, `Reading`, `Alerts`, `Notifications`, `Meeting notes`. At the start of each run, `list_labels`; create any that are missing with `create_label`, then use their IDs.

"Archive" = `unlabel_thread` with `INBOX`. Never trash, never mark spam, never delete.

## Action log

Append one JSON line per action to `logs/actions.jsonl` in this folder:
`{"ts":"<UTC ISO>","thread":"<id>","msg":"<latest message id>","from":"<sender>","subject":"<subject>","bucket":"<bucket>","action":"<replied|drafted|archived|kept>","note":"<short>"}`

## My rulings

Senders I've already ruled on. Apply before classifying. Add a row whenever I tell you.

| Sender | Ruling |
|---|---|
| `example-agency.com` | pitch, archive |

## Sweep

1. Search `in:inbox newer_than:2d` (page through, max 150 threads). Skip a thread whose latest message id is already in the action log.
2. For each thread, take the latest message and put it in the first bucket that fits:

| Bucket | What | Action |
|---|---|---|
| **needs-me** | A real person writing to me about real work: colleagues, customers, investors I talk to, my accountant, lawyers, press, partners, anyone I've emailed before (`in:sent to:<sender>`). Anything about an existing account, contract or invoice that comes from the counterparty itself. Starred threads. | Keep in inbox. |
| **cold-pitch** | Unsolicited pitch from a stranger to get me *customers*: lead gen, outbound/SDR, appointment setting, SEO/AI-SEO, social growth, marketing/growth agencies. Signs: templated flattery, "would it make sense to chat", "does Thursday at 10am work", "reply no thanks". | See **Cold pitches**. |
| **vendor-pitch** | Unsolicited pitch for anything else: design/dev agencies, fundraising brokers, office brokers, SaaS tools, recruiters. The affiliate offer doesn't fit these. If I never replied, prior emails in the thread don't make it real. | Label Cold pitch, archive. No reply. |
| **finance** | Bank, payments and payroll notices, receipts, invoices, statements, payouts. | Label Finance, archive. |
| **alerts** | Monitoring, uptime, cloud and security-tool alerts. | Label Alerts, archive. |
| **meeting-notes** | AI meeting-note emails. | Label Meeting notes, archive. |
| **notifications** | Calendar accepts/declines, doc comment mails, Notion/Figma/etc., verification codes older than 1h, login alerts, product onboarding. | Label Notifications, archive. |
| **reading** | Newsletters, vendor marketing, webinars, product announcements. | Label Reading, archive. |

When unsure, use **needs-me**. A wrongly archived email costs more than one left in the inbox.

3. Log every action.

## Cold pitches

My rule: I only work with growth agencies on an affiliate basis first.

- **First contact** (no message from me in the thread): reply to the latest message, not reply-all, plain text, exactly:

```
Hi - this is YOUR NAME's assistant, replying on their behalf.

YOUR NAME has a different counter-proposal: they pay on an affiliate basis - 100% of any revenue from any clients you get us up to a certain $, then we share the revenue. Thoughts?

--
YOUR NAME's assistant
on behalf of YOUR NAME, YOUR COMPANY
```

  If **Auto-send** is `no`, save it as a draft reply instead (`create_draft` on the thread) and log `drafted`. Then label Cold pitch and archive. If they reply, Gmail puts the thread back in the inbox and the next sweep handles it.
- **They reply after the offer:**
  - Decline, retainer-only, a price list or a booking link → label Cold pitch, archive. No further reply.
  - They accept or want to talk affiliate → keep in inbox, label Cold pitch, flag it in the digest.
- **I already replied** in the thread (anything from me that isn't the template) → keep, don't auto-reply.
- **Guards:** never send the template twice in one thread. At most **Max pitch replies per day** (count today's `replied` + `drafted` in the log); past that, label + archive without replying and mention it in the digest. Never reply to my own domain, to anyone I've emailed before, or to mail sent to a group address (hello@, support@, team@). Never reply to an automated message - an out-of-office, a `noreply@` sender, or one with an `Auto-Submitted` or `X-Autoreply` header - so two bots never answer each other.

## Digest (`--digest`)

What I should know, not what the sweep did. Window: last 24h. About 10 lines — I read it on my phone.

1. **needs-me** threads still in the inbox where the last message isn't from me. One line each: who, what they want, how long it has waited. Oldest first. Max 6, then "+N more".
2. **Pitch replies** that want to talk affiliate.
3. **Finance worth a look:** a single charge over $1,000, a failed payment, a new vendor charging for the first time, a tax item. Skip routine charges.
4. **Alerts worth a look:** anything still firing, a new alert type, a new-device login.
5. Footer: `handled: N pitches answered, N archived`.

```
📬 Inbox — {Ddd DD Mon}

Needs you:
- {Name} ({org}) - {ask} · {age}

Worth knowing:
- {item}

handled: {n} pitches answered, {n} archived
```

Drop an empty section. If nothing needs me, say "Nothing needs you." and keep the footer.

With `--slack`, send it with `slack_send_message` to my Slack member ID.
