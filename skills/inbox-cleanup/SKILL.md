---
name: inbox-cleanup
description: Dig a buried inbox out - separate scams and spam from legitimate bulk mail, block scam senders, clear old notifications under a keep-one-month rule, mark reviewed mail read, and surface the few emails that actually need action. Written for Outlook / Microsoft 365 (Graph API or Outlook on the web); the method carries to any mailbox. Use for "clean up my inbox", "I have too much spam", "go through my unread", or "block these scammers".
---

# Inbox cleanup

## The shape of a buried inbox (learn this first)

In a real 1,400-message inbox, **most of the volume wasn't spam.** One legitimate sender
the owner had signed up for was ~40% of it. The dangerous mail was a *small* number of
well-disguised scams hiding inside the noise. So:

1. **Separate before you destroy.** Group by sender and by kind (scam, promo, notification,
   record, conversation) and show the owner the groups before anything moves.
2. **Legit bulk mail is fixed at the source.** Change the frequency settings in that
   account, or unsubscribe. Blocking it kills the alerts the owner actually wants.
3. **Scams get blocked by domain**, with a rule, and written down (below).

## What never gets touched

Receipts, statements, bills, payment and transfer confirmations, tax and legal notices,
tickets for upcoming events, anything tied to an open issue, and real conversations.
(Receipts and confirmations can go once they're in a local log. See "Log first" below.)
A receipt riding on an otherwise junky sender is still a receipt: filter by **subject**,
not by sender, for those.

## The keep-one-month rule for notifications

Older than ~30 days and not a record -> Deleted Items (recoverable, not purged):
- order shipped / delivered notices, sign-in and new-device alerts, "security alert"
  copies, expired one-time codes, password-reset mail
- card alerts like "card not present", weekly snapshots, "large purchase approved"
  (keep statements and declines)
- reminders for events already past, appointment reminders, outage alerts
- newsletters and webinar invites from otherwise-important senders (keep their real notices)

## Log first, then clean harder (the "keep only what's worth reading" pass)

Two careful passes can still leave an inbox that *looks* full: hundreds of receipts,
payment confirmations and "your statement is ready" notices, each one individually worth
keeping. The fix is to **write every email to a local log first** (one line per email:
date, sender, subject, first few hundred characters, a rough category), commit that file,
and only then clean. Once the information lives in the log, the mailbox can keep just what
needs reading:

- **Keep:** unread to-dos, pinned or flagged mail, upcoming trips / tickets / events, tax
  and legal papers, certificates, records of open issues, the latest bill from each
  biller, and every real conversation.
- **Move out, at any age:** receipts, payment and transfer confirmations, statement-ready
  notices, sign-in and security alerts, marketing, newsletters. All still findable with
  `grep` in the log, and still in Deleted Items for a while.

Bonus: pull the promo emails out of the log into a **deals list** (store, month, size of
the offer). It becomes a reference for when a store usually runs its sales.

Blank out one-time codes in the log. A code is useless once it expires, but it still
shouldn't sit in a file.

## Scams to recognize

- **Fake government filing services.** Business owners get official-looking mail citing
  their *real* company registration number, warning of dissolution or a late fee, and
  asking them to "file the annual report" or a "mandatory beneficial ownership (BOI)
  report" through a third party. The real filing happens only on the state's own site.
  These rings register new lookalike domains constantly, so a block list for them is
  **always out of date**. Block each new domain as it shows up.
- **Brand impersonation** (a bank or brokerage name on a strange domain), **fake payment
  reports and cold "invoice" pitches**, **crypto and "card" offers**.
- **Legit-sender phishing:** a real platform's sending service (e.g. a SaaS trial email)
  carrying a link to an unrelated domain. Don't block the platform; move that one to Junk.

## Block list: keep it in a file

Create rules named `Spam - <what it is>` (sender-domain contains -> move to Junk or
delete, mark read, stop processing) and **record every rule in a version-controlled file**
(`blocklist.md`: rule name, domains, action, date). Mailbox rules get wiped by resets,
migrations and "clean up my rules" moments; the file lets you rebuild them in minutes.

**Don't create folder-sorting rules** unless the owner asks for them. Auto-filing mail into
folders is the most common reason people stop seeing their own mail.

## Microsoft Graph gotchas (all learned the hard way)

- **Search never enumerates a folder.** A search returns a subset (~100) and which subset
  depends on the query. Treat search counts as samples; verify with **folder counts**.
- **`isRead eq false` / `isread:false` lists unread mail directly.** Much faster than
  sampling the whole inbox.
- **Date slicing works:** `received<MM/DD/YYYY` reaches older mail that newest-first
  searches never show. Combining a text query *with* a date query returned 400; filter
  dates locally instead.
- **Throttling (`429 ApplicationThrottled / MailboxConcurrency`) is per mailbox.** Send
  **one call at a time**. Parallel calls 429 together.
  - Mark-as-read: **4 messages per call** went through almost every time; 5 failed about
    half the time; 10 and 25 failed.
  - Moves: 5 per call. **A 429 on a move often still moved the whole batch**, so the next
    call on the same IDs 404s. After any 429 or 404, fetch fresh IDs.
  - A 503 is transient; resend the same batch.
- **For hundreds of moves, work in rounds.** Batches of ~8, fired back to back, all 429,
  but each still moved roughly half its messages. The loop that cleared 300+: send the
  batches -> pull the inbox fresh -> diff it against your planned ID list -> resend only
  what's still there. Never resend an ID that already moved; one stale ID can fail the
  whole batch. About six rounds did it.
- **Verify at the end:** folder counts, plus date-sliced searches matched against your
  planned list, catch the ~10% a throttled run silently skips.
- An open Outlook-on-the-web tab seems to count against the same concurrency limit.
  Park it on another page while the API runs.

## Outlook on the web (when there's no API)

The new Outlook for Windows has no COM automation. Outlook on the web does bulk work well:
- Search `from:a.com OR from:b.com`, `from:x NOT subject:payment`, or
  `(from:x subject:"offer") OR (from:y subject:promo)`.
- Set scope to **Current folder** (the default "All folders" pulls in Deleted Items).
- Click the first result, Ctrl+A. The banner "All search results selected" means a
  true select-all. **Delete all** -> the dialog states the count: read it.
- Re-run until "No more results"; a big delete can leave a second page.
- **Before every typed search, confirm the search box has focus.** After a delete, focus
  leaves the box, and typing fires single-key shortcuts. In one run that opened three
  blank compose windows. Nothing was sent, but it could have been worse.
- Never go through a sign-in, passkey or recovery prompt for the owner.

## Surfacing what matters

The payoff of a cleanup is the short list at the end: the few emails that need the owner.
Flag them in the mailbox and report them plainly: account deadlines ("log in by the 30th or
the balance goes to the state"), settlement claims, fee warnings, "your saved payment
methods were removed, re-enroll AutoPay". Put dated ones on the calendar.
