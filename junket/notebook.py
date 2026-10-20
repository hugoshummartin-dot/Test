"""The student's agenda and address book: what you take home from a junket."""

from dataclasses import dataclass, asdict


@dataclass
class Event:
    title: str
    venue: str
    day: int  # days after the cocktail
    host: str
    pitch: str  # how the host sold it to you
    worthwhile: bool = False  # hidden until you actually go


@dataclass
class Contact:
    name: str
    occupation: str  # what they *told* you they do
    met_at: str
    note: str
    useful: bool = False  # hidden until it pays off (or doesn't)


class Agenda:
    def __init__(self):
        self.events = []

    def add(self, event):
        self.events.append(event)
        self.events.sort(key=lambda e: e.day)

    def __len__(self):
        return len(self.events)

    def render(self):
        if not self.events:
            return "Your agenda is empty."
        lines = ["AGENDA — proposed events"]
        for e in self.events:
            lines.append(f"  in {e.day:>2} day{'s' if e.day != 1 else ' '}  {e.title} @ {e.venue}")
            lines.append(f"              invited by {e.host}: \"{e.pitch}\"")
        return "\n".join(lines)

    def to_dict(self):
        return [asdict(e) for e in self.events]


class AddressBook:
    def __init__(self):
        self.contacts = []

    def add(self, contact):
        if any(c.name == contact.name for c in self.contacts):
            return False
        self.contacts.append(contact)
        return True

    def __len__(self):
        return len(self.contacts)

    def render(self):
        if not self.contacts:
            return "Your address book is empty."
        lines = ["ADDRESS BOOK"]
        for c in sorted(self.contacts, key=lambda c: c.name.split()[-1]):
            lines.append(f"  {c.name} — {c.occupation}  (met at {c.met_at})")
            lines.append(f"      note: {c.note}")
        return "\n".join(lines)

    def to_dict(self):
        return [asdict(c) for c in self.contacts]
