# Digging out of 1,400 emails

**Skill:** [`inbox-cleanup`](../skills/inbox-cleanup/SKILL.md)

## The problem

Two Outlook mailboxes. The main one: about 1,470 messages, 1,170 unread. The owner had
stopped trusting it because years of auto-filing rules were sorting mail into folders
they never opened. Forty of those rules were filing banking mail into a folder that
**no longer existed**.

## What the agent did, in passes

1. **Deleted the foldering rules** (with the owner's go-ahead) and emptied the folders
   back into the Inbox. Mail lands where it can be seen.
2. **Measured before touching anything.** One sender was about 40% of the inbox, and it
   was mail the owner *wanted* (event ticket alerts). That's a frequency setting, not a
   block.
3. **Found the real threats:** a ring of fake "state annual report filing" services
   citing the owner's actual business registration number and threatening a late fee.
   Each got a block rule, and every rule got written into a version-controlled
   `blocklist.md`, because the list had once been wiped out along with the other rules.
4. **Cleared notifications with a keep-one-month rule:** old shipping notices, expired
   codes, sign-in alerts, past-event reminders. Receipts, statements, bills and tickets
   were never touched.
5. **Reviewed every unread email** and marked the reviewed ones read: 285 -> 29 and
   79 -> 1. What stayed unread was deliberate: business mail, and a handful of items
   that needed a human.

## What was actually hiding in there

The whole point: a short list of things that mattered. A brokerage saying *log in by the
30th or the dormant balance goes to the state.* A utility saying *your saved payment
methods were removed, re-enroll AutoPay.* A class-action settlement with a claim
deadline, which went on the calendar. An HSA that had never been activated. Each was
flagged in the mailbox and reported in plain words.

## What fought back

- **API throttling.** Microsoft Graph throttles per mailbox. Parallel calls failed
  together; mark-as-read worked reliably at 4 messages per call and not at 25. A
  throttled *move* often still completed, so retrying the same IDs caused errors. The
  fix was one call at a time, fresh IDs after any error, and folder counts at the end.
- **Search is a sample, not a list.** Date-sliced searches found alerts the first sweep
  missed.
- **Outlook on the web shortcuts.** Typing a search after focus had left the search box
  opened three blank compose windows. Now the agent checks focus before every search.
