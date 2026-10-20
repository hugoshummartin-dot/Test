# Reticular: Networking Simulator

## Pocket Expat (phone game)

`pocket-expat/index.html` is a mobile-first web game built on the cocktail below. You're a
student abroad, and the gacha is a departures board of networking events around the world.

- **Draw** events with miles (100 per draw, 900 for ten). Tiers: N 55%, R 30%, SR 12%, SSR 3%.
  SR or better is guaranteed every 10 draws and SSR within 60.
- Rarer events have bigger rooms with more people worth meeting: 5% at N up to 30% at SSR.
- **Attend** an event from your agenda. This jumps the calendar to its day, and anything
  scheduled before then is missed. Flights cost 100 miles unless your host covers them.
- Each event is the 60-minute cocktail: approaching someone costs 5 minutes and each
  conversation step costs 10.
- **The morning after:** the cards you collected flip over to show their rarity. Interesting
  people (R/SR/SSR) invite you to good events in other cities with the flight paid. Schmucks
  (N) invite you to pointless ones.
- **Passport:** stamps for each city, plus an expat level based on reach (R = 1, SR = 3, SSR = 8).

Open the file in a phone browser to play. Progress is saved in that browser only.

## The cocktail (text prototype)

You're a student who has talked their way into a junket. The goal: leave with contacts
who can actually take you places.

This first feature is **the cocktail** — a 60-minute, text-only networking game.

## Play

```sh
python3 -m junket              # random room
python3 -m junket --seed 7     # reproducible room
python3 -m junket --save notebook.json   # keep your agenda + address book
```

No dependencies beyond Python 3.9+.

## Rules

- The cocktail runs 19:00–20:00. Only actions move the clock:
  - **approach** someone: 5 min
  - **talk** (move the conversation on a step): 10 min
  - looking around, checking your agenda/address book: free
- 100 guests. **20** have something to offer; **80** are clueless (nice, pointless) or
  useless (pushy, and they'll drag you to pointless events and fruitless endeavours).
- Until you've talked to someone you only know what they **look like**. Looks lean a
  little by type (who's talking quietly with the host, who's handing out cards to anyone)
  but never give it away.
- People leave as the evening goes on — and the interesting ones are busy.
- Conversations go: introduction → what they do → substance (cards change hands) →
  invitation. Useless people skip ahead: card first, invitation next. Eagerness is a tell.
- Cards land in your **address book**, invitations in your **agenda**. The morning-after
  debrief reveals which were worth it.

## Commands

| command | cost | |
|---|---|---|
| `room [word]` | free | who's still here, optionally filtered (`room host`) |
| `look N` | free | closer look at guest #N |
| `approach N` | 5 min | introduce yourself |
| `talk` | 10 min | push the conversation forward |
| `leave` | free | walk away from the current conversation |
| `agenda` / `contacts` | free | your notebook |
| `home` | — | leave early |

## Code

- `junket/people.py` — guest generation, appearance pools, roles and their events
- `junket/notebook.py` — `Agenda`, `AddressBook`, `Event`, `Contact`
- `junket/cocktail.py` — the timed scene; UI-free (`Cocktail.do(command) -> str`)
- `junket/__main__.py` — terminal front end

Tests: `python3 -m unittest`
