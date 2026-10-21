# Reticular: Networking Simulator

## Phone game (`pocket-expat/index.html`)

A mobile-first web build blending the Pocket Expat prototype with the Reticular brief.
Open the file in a phone browser to play. Progress is saved in that browser only.

- **Currency:** business cards. A draw costs 100 and ten draws cost 900. Flights to other
  cities cost 100 unless your host covers them, and waiting a day earns 50.
- **Draws:** events at tiers N 55%, R 30%, SR 12% and SSR 3%. SR or better is guaranteed
  within 10 draws and SSR within 60. Speaking engagements are a rare separate result.
- **Event length depends on tier:** N 30 min, R 45, SR 90, SSR 120.
- **Conversations:** introducing yourself costs 1 min, and each further step doubles
  (2, 4, 8 min). "Your read" is a gauge that updates after each step. It is noisy at
  first and gets more accurate the longer you talk.
- **Speaking engagements** are drawn at your highest unlocked level. You record their
  outcome in a track record, and enough successes at one level unlock the next.
  *Placeholders until specified:* a 2% draw rate, 3 levels, and 3 successes to unlock the
  next level. The performance minigame is not defined yet, so for now you record each
  outcome by hand.
- **The morning after:** your contact cards flip to reveal their rarity, and invitations
  join your agenda. The passport shows stamps, your level and your track record.

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
