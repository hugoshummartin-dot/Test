"""A 60-minute cocktail: every action costs time, so choose who to talk to wisely.

Conversation stages for each guest:
  0  unmet          — you only know what they look like
  1  approached     — (5 min) you know their name and get a first impression
  2  small talk     — (10 min) they tell you what they do (or what they claim to do)
  3  getting real   — (10 min) the substance; cards change hands
  4  invitation     — (10 min) they propose an event for your agenda
Pushy useless people skip ahead: cards at stage 2, invitations at stage 3.
"""

import random

from .notebook import Agenda, AddressBook, Contact
from .people import INTERESTING, CLUELESS, USELESS, generate_guests

APPROACH_COST = 5
TALK_COST = 10
DURATION = 60
START_HOUR, START_MINUTE = 19, 0
MAX_STAGE = 4

HELP = """\
Commands (free unless noted):
  room [word]     list who is still in the room (optionally filter, e.g. 'room suit')
  look N          take a closer look at guest #N
  approach N      walk up to guest #N and introduce yourself   (5 min)
  talk            move the current conversation forward         (10 min)
  leave           excuse yourself from the current conversation
  agenda          show proposed events
  contacts        show your address book
  time            show the clock
  home            call it a night early
  help            show this help"""


class Cocktail:
    def __init__(self, seed=None, venue="the Junket cocktail", total=100, interesting=20):
        self.rng = random.Random(seed)
        self.venue = venue
        self.guests = generate_guests(self.rng, total=total, interesting=interesting)
        self.by_id = {g.pid: g for g in self.guests}
        self.minute = 0
        self.current = None  # the guest you are talking to
        self.agenda = Agenda()
        self.contacts = AddressBook()
        self.over = False
        self._left = set()

    # --- clock -----------------------------------------------------------------
    def clock(self, minute=None):
        m = START_MINUTE + (self.minute if minute is None else minute)
        return f"{START_HOUR + m // 60:02d}:{m % 60:02d}"

    @property
    def remaining(self):
        return DURATION - self.minute

    def status_line(self):
        who = f" | talking to {self.current.name}" if self.current else ""
        return f"[{self.clock()} — {self.remaining} min left{who}]"

    # --- room ------------------------------------------------------------------
    def present(self):
        return [g for g in self.guests if g.pid not in self._left]

    def _advance(self, cost):
        self.minute += cost
        notes = []
        others = []
        for g in [g for g in self.present() if g.leaves_at <= self.minute]:
            self._left.add(g.pid)
            if g is self.current:
                notes.append(f"{g.name} glances at their watch, apologises, and heads for the coat check.")
                self.current = None
            elif g.stage > 0:
                notes.append(f"{g.name} has left.")
            else:
                others.append(g)
        if others:
            ids = ", ".join(f"#{g.pid}" for g in others)
            notes.append(f"{len(others)} {'person has' if len(others) == 1 else 'people have'} left the room ({ids}).")
        if self.minute >= DURATION:
            self.over = True
            notes.append("The lights come up. The cocktail is over.")
        return notes

    def _guest(self, arg):
        try:
            pid = int(arg.lstrip("#"))
        except (ValueError, AttributeError):
            return None, "Which guest? Give a number, e.g. 'approach 12'."
        g = self.by_id.get(pid)
        if g is None:
            return None, f"There is no guest #{pid}."
        if pid in self._left:
            return None, f"#{pid} has already left."
        return g, None

    # --- actions ---------------------------------------------------------------
    def room(self, word=""):
        people = self.present()
        if word:
            people = [g for g in people if word.lower() in g.label().lower()]
        if not people:
            return "Nobody matches that." if word else "The room is empty."
        lines = [f"In the room ({len(people)}{' matching' if word else ''}):"]
        for g in people:
            mark = "*" if g is self.current else " "
            lines.append(f" {mark}#{g.pid:<3} {g.label()}")
        return "\n".join(lines)

    def look(self, arg):
        g, err = self._guest(arg)
        if err:
            return err
        text = g.details
        if g.stage > 0:
            text = f"{g.name}. {text}"
        if g.stage >= 2:
            text += f"\nThey told you: \"{g.claim}\""
        return text

    def approach(self, arg):
        g, err = self._guest(arg)
        if err:
            return err
        if g is self.current:
            return f"You're already talking to {g.name}."
        if self.remaining < APPROACH_COST:
            return "There isn't enough time left to approach anyone."
        if g.stage == 0:
            g.stage = 1
            text = f"You make your way over to #{g.pid}. \"Hi, I'm {g.name}.\"\n{g.small_talk}"
        else:
            text = f"You catch {g.name} again. They remember you."
        self.current = g
        return "\n".join([text] + self._advance(APPROACH_COST))

    def leave(self):
        if not self.current:
            return "You're not talking to anyone."
        name, self.current = self.current.name, None
        return f"You excuse yourself from {name}."

    def talk(self):
        g = self.current
        if not g:
            return "You're not talking to anyone. Approach someone first."
        if self.remaining < TALK_COST:
            return "There isn't enough time left for a real conversation."
        lines = self._progress(g)
        return "\n".join(lines + self._advance(TALK_COST))

    def _progress(self, g):
        if g.stage >= MAX_STAGE:
            return [f"The conversation with {g.name} is running dry. You trade pleasantries about the weather."]
        g.stage += 1
        lines = []
        if g.stage == 2:
            lines.append(f"You ask what they do. \"{g.claim}\"")
            if g.kind == USELESS:
                lines.append(self._card(g, g.claim, "They press a business card into your hand before you can ask more."))
        elif g.stage == 3:
            lines.append(f"\"{g.substance}\"")
            if g.kind == INTERESTING:
                lines.append(self._card(g, g.real_role, f"They hand you a plain card: {g.real_role}."))
            elif g.kind == CLUELESS:
                lines.append(self._card(g, g.claim, "You swap numbers, mostly out of politeness."))
            else:
                lines.append(self._invite(g))
        elif g.stage == 4:
            if g.kind == USELESS:
                lines.append(f"{g.name} repeats the pitch, louder. You learn nothing new.")
            else:
                lines.append(self._invite(g))
        return lines

    def _card(self, g, occupation, text):
        if g.gave_card:
            return text
        g.gave_card = True
        self.contacts.add(Contact(name=g.name, occupation=occupation, met_at=self.venue,
                                  note=g.substance, useful=g.is_useful))
        return text + " (added to your address book)"

    def _invite(self, g):
        if g.gave_invite or g.event is None:
            return ""
        g.gave_invite = True
        self.agenda.add(g.event)
        e = g.event
        return (f"\"You should come to the {e.title} — {e.venue}, in {e.day} days. {e.pitch}\""
                " (added to your agenda)")

    # --- dispatch --------------------------------------------------------------
    def do(self, line):
        parts = line.strip().split(maxsplit=1)
        if not parts:
            return ""
        cmd, arg = parts[0].lower(), (parts[1] if len(parts) > 1 else "")
        if cmd in ("room", "r", "ls"):
            return self.room(arg)
        if cmd in ("look", "l"):
            return self.look(arg)
        if cmd in ("approach", "a", "go"):
            return self.approach(arg)
        if cmd in ("talk", "t"):
            return self.talk()
        if cmd in ("leave", "bye"):
            return self.leave()
        if cmd in ("agenda", "ag"):
            return self.agenda.render()
        if cmd in ("contacts", "c", "book"):
            return self.contacts.render()
        if cmd in ("time",):
            return self.status_line()
        if cmd in ("help", "h", "?"):
            return HELP
        if cmd in ("home", "quit", "q", "exit"):
            self.over = True
            return "You collect your coat and head home."
        return f"Unknown command '{cmd}'. Type 'help'."

    # --- the morning after -----------------------------------------------------
    def debrief(self):
        lines = ["", "=== THE MORNING AFTER ===",
                 f"You spent {self.minute} minutes at {self.venue}.",
                 f"You met {sum(1 for g in self.guests if g.stage > 0)} of {len(self.guests)} guests."]
        if self.contacts.contacts:
            lines.append("In hindsight, your new contacts:")
            for c in self.contacts.contacts:
                verdict = "can take you places" if c.useful else "a dead end"
                lines.append(f"  {'+' if c.useful else '-'} {c.name} ({c.occupation}) — {verdict}")
        if self.agenda.events:
            lines.append("In hindsight, the events in your agenda:")
            for e in self.agenda.events:
                verdict = "worth going" if e.worthwhile else "a waste of an evening"
                lines.append(f"  {'+' if e.worthwhile else '-'} {e.title} ({e.host}) — {verdict}")
        missed = [g for g in self.guests if g.kind == INTERESTING and not g.gave_card]
        good = sum(c.useful for c in self.contacts.contacts) + sum(e.worthwhile for e in self.agenda.events)
        lines.append(f"Useful contacts + worthwhile invitations: {good}. "
                     f"Interesting people you never got to: {len(missed)} of "
                     f"{sum(1 for g in self.guests if g.kind == INTERESTING)}.")
        return "\n".join(lines)

    def to_dict(self):
        return {"agenda": self.agenda.to_dict(), "contacts": self.contacts.to_dict()}
