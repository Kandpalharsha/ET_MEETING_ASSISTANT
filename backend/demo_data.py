ET_TRANSCRIPT = """
Editorial Planning Meeting — Economic Times Digital
Date: March 23, 2026 | 10:00 AM IST
Attendees: Rakesh Sharma (Senior Editor), Priya Nair (Bureau Chief),
           Arjun Mehta (Correspondent), Vikram Iyer (Tech Lead),
           Sunita Rao (Legal/Compliance), Meera Joshi (Events),
           Ravi Krishnan (Finance)

Rakesh: Let's start. Top priority this week is the Union Budget impact analysis.
We've decided it goes live Tuesday, April 1st — that's locked in.
Arjun, you're on ground reporting. Can you file the first draft by March 29?

Arjun: Yes, I'll have it ready. Should I include the MSME sector angle?

Rakesh: Absolutely, make it the lead angle. Priya, once Arjun files,
editorial review needs to be done by March 30th. Can you own that?

Priya: Sure. I'll pull in the Mumbai bureau for regional data points too.

Rakesh: Good. Now — Sunita, the fintech regulatory piece we're running on Friday.
Legal needs to clear it before publish. There are some RBI circular references
from February that need fact-checking against the actual text.

Sunita: I'll handle the compliance review. I need until March 28th.
The February RBI circular on payment aggregators — I'll flag anything
that looks like a misquote.

Rakesh: Perfect. Vikram, there was an outage on the ET Markets live feed
yesterday during the Sensex rally. That websocket reconnection bug cannot
happen during Budget day coverage — we'll have 10x normal traffic.

Vikram: Understood. My team will have the websocket fix patched and tested
by March 27th. I'll also set up the load monitoring dashboards for Budget day
by April 1st.

Meera: Quick flag — registration confirmation emails for the ET Wealth Summit
are bouncing. About 200 registrations haven't gotten their confirmation.
The email delivery pipeline needs a fix.

Vikram: That's on the tech side. I'll look at it — same team,
should be sorted by March 26th.

Rakesh: Ravi — we need finance sign-off on the Budget special supplement
sponsorship packages. There are three advertisers waiting on confirmed rates.

Ravi: I'll get the approval done by March 25th and send the confirmed
rate cards to the sales team.

Priya: One more — TRAI announced a new AI content disclosure policy last week.
Our editorial style guide needs updating before we publish any AI-assisted content.

Sunita: That's on me too. I'll draft the updated disclosure guidelines
and circulate for team review by March 31st.

Rakesh: That covers everything. Budget coverage is the critical path —
nothing should block April 1st. Let's reconvene April 5th for post-Budget debrief.
"""

DEMO_SCRIPT = """
╔══════════════════════════════════════════════════════════╗
║         ET EDITORIAL WORKFLOW — DEMO SCRIPT (3 min)      ║
╚══════════════════════════════════════════════════════════╝

00:00  Upload the ET_TRANSCRIPT
       → Extraction agent parses it (Groq Llama 3.3 70B)
       → DuckDuckGo searches for related ET Budget headlines
       → Audit log: "8 tasks found, 1 ambiguous owner (email delivery pipeline)"

00:40  Escalation agent fires on ambiguous task
       → Pass 1: "email" + "delivery" → org chart → Vikram Iyer
       → Audit log: "Resolved via ET org chart. No LLM call needed."

01:10  All 8 tasks appear on the board
       → Owners, deadlines, priorities, categories all populated
       → "Mock Slack notifications sent to each owner"

01:40  Click "Simulate Stall" on Sunita's compliance review task
       → Tracker detects: 48h no progress, deadline approaching
       → Audit log: "STALLED — escalating to Rakesh Sharma with full context"
       → Manager notification mock shown

02:20  Scroll the audit trail
       → Show every agent decision with reasoning and timestamp
       → Count: "8 tasks created, 7 autonomous steps, 1 human escalation"

02:45  Close line:
       "From a 15-minute editorial meeting to 8 tracked tasks,
        one autonomous recovery, and a full audit trail —
        with one human notification sent only when genuinely needed.
        This is what ET's editorial operations look like when
        meetings manage themselves."
"""
