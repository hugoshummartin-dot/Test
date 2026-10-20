"""The cast of a junket: who is in the room, what they look like, what they really are.

Three kinds of people:
  * interesting — can genuinely take you places (20 of 100 by default)
  * clueless    — pleasant, but know nothing and can do nothing for you
  * useless     — big talkers who drag you into pointless events and fruitless endeavours

Appearances are drawn from shared pools with weights that lean slightly by kind, so
looks carry a hint but never a guarantee.
"""

import random
from dataclasses import dataclass
from typing import Optional

from .notebook import Event

INTERESTING = "interesting"
CLUELESS = "clueless"
USELESS = "useless"

FIRST_NAMES = [
    "Ada", "Alain", "Amara", "Anouk", "Arjun", "Beatriz", "Bram", "Camille", "Chiara", "Dario",
    "Delphine", "Dmitri", "Elena", "Emeka", "Esther", "Fabian", "Farah", "Felix", "Greta", "Hamid",
    "Hana", "Hugo", "Ines", "Isak", "Jonas", "Josephine", "Kenji", "Lars", "Leila", "Luca",
    "Mai", "Malik", "Margot", "Mateo", "Mira", "Nadia", "Nico", "Noor", "Olga", "Oscar",
    "Paloma", "Pieter", "Priya", "Quentin", "Rafael", "Rosa", "Sacha", "Selin", "Soren", "Tariq",
    "Thea", "Tomas", "Ugo", "Valentina", "Viktor", "Wanda", "Xavier", "Yara", "Yusuf", "Zoe",
]
LAST_NAMES = [
    "Albers", "Bakker", "Benali", "Castell", "Costa", "Dubois", "Eriksen", "Ferreira", "Fontaine", "Gallo",
    "Hartmann", "Haddad", "Ivanova", "Jansen", "Kaur", "Keller", "Laurent", "Lindqvist", "Marchetti", "Moreau",
    "Nakamura", "Novak", "Okafor", "Oyelaran", "Petrov", "Quist", "Rahman", "Rossi", "Santos", "Schmidt",
    "Silva", "Takahashi", "Toussaint", "Ullman", "Varga", "Vermeulen", "Weber", "Wright", "Yilmaz", "Zanetti",
]

# Appearance pools: (text, weight if interesting, weight if clueless, weight if useless)
AGES = [
    ("young", 1, 3, 3),
    ("thirty-something", 2, 2, 3),
    ("middle-aged", 3, 2, 2),
    ("grey-haired", 3, 2, 1),
    ("elderly", 1, 2, 0.5),
]
FIGURES = [("man", 1, 1, 1), ("woman", 1, 1, 1), ("person", 0.3, 0.3, 0.3)]
OUTFITS = [
    ("a sharply tailored charcoal suit", 3, 1, 3),
    ("an understated navy blazer", 4, 2, 1),
    ("a crumpled linen jacket", 2, 3, 1),
    ("a sequinned jacket", 1, 1, 4),
    ("a black turtleneck", 3, 1, 2),
    ("jeans and a band T-shirt", 1, 3, 1),
    ("a silk dress", 2, 2, 2),
    ("a velvet smoking jacket", 1, 1, 3),
    ("a plain white shirt", 1, 3, 1),
    ("a vintage tweed coat", 2, 2, 1),
    ("a logo-covered designer hoodie", 0.5, 1, 4),
    ("a plain grey cardigan", 2, 3, 1),
    ("an elegant black dress", 3, 2, 2),
    ("a loud floral shirt", 1, 2, 3),
]
BEHAVIOURS = [
    ("talking quietly with the host", 5, 0.5, 1),
    ("loudly telling a story to a shrinking circle", 0.5, 1, 5),
    ("hovering by the canapés", 0.5, 4, 2),
    ("glancing at the door as if about to leave", 3, 1, 1),
    ("handing out business cards to anyone nearby", 0.5, 0.5, 5),
    ("listening more than talking", 4, 2, 0.5),
    ("scrolling through their phone in a corner", 1, 4, 2),
    ("laughing a bit too loudly", 0.5, 2, 3),
    ("being greeted by several people in turn", 4, 1, 2),
    ("studying the artwork on the walls", 2, 3, 1),
    ("on what looks like a third glass of champagne", 0.5, 3, 3),
    ("nursing a sparkling water", 3, 2, 1),
    ("taking selfies with the room in the background", 0.2, 2, 4),
    ("waiting for someone to talk to", 1, 4, 1),
]
ACCESSORIES = [
    ("an expensive but discreet watch", 3, 1, 2),
    ("a lanyard from an unrelated conference", 0.5, 3, 2),
    ("reading glasses pushed up on their head", 2, 2, 1),
    ("a gold chain", 0.5, 1, 3),
    ("a battered leather notebook", 3, 2, 1),
    ("a tote bag full of flyers", 0.2, 1, 4),
    ("a lapel pin you don't recognise", 2, 1, 2),
    ("a phone in each hand", 1, 0.5, 3),
    ("nothing remarkable", 2, 3, 2),
]

# Roles: what they claim to do, what they say once you dig, what they can really offer,
# and the event they invite you to: (title, venue, pitch).
INTERESTING_ROLES = [
    ("I work with pictures, mostly.", "Director of a contemporary art gallery",
     "We're always looking for sharp young people for the next show.",
     "a paid assistant job on the next exhibition",
     ("Private preview of the spring exhibition", "the gallery, after hours", "Come early — the artist will be there.")),
    ("I invest a little.", "Partner at a venture capital fund",
     "Our fund backs student founders. Send me what you're working on.",
     "a real meeting with an investor",
     ("Founders' breakfast", "the fund's office", "Six founders, one table. Bring your idea.")),
    ("I read a lot for a living.", "Senior editor at a publishing house",
     "We need readers who can tell a good manuscript from a bad one.",
     "freelance manuscript reports, and a foot in publishing",
     ("Editorial meeting open to guests", "the publisher's offices", "Sit in and see how a list gets built.")),
    ("I put on shows.", "Theatre producer",
     "There's always a production assistant slot for someone keen.",
     "a production assistant role",
     ("Final dress rehearsal", "the municipal theatre", "Watch from the wings — then meet the cast.")),
    ("I run a small lab.", "Head of a university research lab",
     "We take one or two student researchers a year. Most never ask.",
     "a research internship",
     ("Lab seminar and drinks", "the science faculty", "Present yourself to the team.")),
    ("I'm with the embassy.", "Chief of staff to an ambassador",
     "Our cultural programme takes interns every term.",
     "an embassy internship and a lot of introductions",
     ("National day reception", "the ambassador's residence", "Half the city's decision-makers will be there.")),
    ("I draw buildings.", "Founder of an architecture studio",
     "We're short of hands for a competition entry.",
     "a paid competition sprint at a respected studio",
     ("Studio crit night", "the studio", "Bring a portfolio; we'll tear it apart kindly.")),
    ("I feed people.", "Restaurateur with three acclaimed restaurants",
     "Half my investors I met at my own tables.",
     "a table where real deals get made",
     ("Chef's table dinner", "the flagship restaurant", "Eight seats. I choose who sits next to whom.")),
    ("I write things down.", "Investigative journalist at a national paper",
     "I need someone who can dig through records patiently.",
     "a research assistant role and a byline",
     ("Newsroom open evening", "the paper's newsroom", "See how a front page is fought over.")),
    ("I watch films.", "Programmer for an international film festival",
     "Our selection committee needs pre-screeners.",
     "an accreditation and a pre-screener job",
     ("Industry screening", "the festival cinema", "Distributors, directors, and a bar afterwards.")),
    ("I sold a company once.", "Serial founder who exited a startup",
     "I like helping people who ask good questions.",
     "a mentor with a deep address book",
     ("Angel syndicate dinner", "a private members' club", "Sit next to me, keep your ears open.")),
    ("I look after old things.", "Chief curator at the national museum",
     "Our archive project needs research volunteers — paid ones, now.",
     "a paid archive post",
     ("Behind-the-scenes archive tour", "the museum stores", "Things nobody else gets to see.")),
    ("I give money away.", "Programme officer at a large foundation",
     "Our student grants go unclaimed because nobody applies.",
     "a grant application that will actually be read",
     ("Grantee showcase", "the foundation's hall", "Meet the people we fund, and their funders.")),
    ("I argue for a living.", "Partner at an international law firm",
     "Our summer programme fills from referrals.",
     "a referral for a summer associate post",
     ("Firm summer reception", "the firm's rooftop", "The recruiting partners will be there.")),
    ("I find people talent.", "Talent agent at a major agency",
     "I can always use an assistant who knows the scene.",
     "an assistant job inside a top agency",
     ("Agency showcase", "a small club downtown", "Next year's names, tonight.")),
    ("I wave a stick.", "Principal conductor of the city orchestra",
     "Our outreach team is desperate for organised people.",
     "an outreach coordinator role",
     ("Open rehearsal", "the concert hall", "Come backstage at the interval.")),
    ("I do clothes.", "Creative director at a fashion house",
     "Our studio takes two interns a season.",
     "a studio internship",
     ("Atelier presentation", "the atelier", "Small, invitation only.")),
    ("I cut people open.", "Chief of surgery at the university hospital",
     "Our innovation unit wants students from outside medicine.",
     "a place on a hospital innovation project",
     ("Innovation day", "the hospital auditorium", "Clinicians pitching to engineers — you'd fit right in.")),
    ("I break computers, professionally.", "CTO of a fast-growing software company",
     "We hire juniors on recommendation, not CVs.",
     "a recommendation that skips the CV pile",
     ("Engineering open house", "the company HQ", "Meet the team leads over pizza.")),
    ("I listen to records.", "A&R lead at a record label",
     "I need scouts who actually go to gigs.",
     "a paid scouting gig",
     ("Label showcase night", "a basement venue", "Three acts we're about to sign.")),
]

USELESS_ROLES = [
    ("I'm in venture — well, angel-ish.", "Has never invested a cent",
     "I could put you in front of my network. Huge network.", "nothing but a lot of LinkedIn requests",
     ("Exclusive Founders' Mixer", "a bowling alley", "Everyone who's anyone. Entry is only €40.")),
    ("Brand strategist, influencer, visionary.", "Has 900 followers",
     "We should collab. Seriously. My audience would love you.", "an unpaid 'collab'",
     ("Content creators' brunch", "a café that hasn't agreed to host it", "Bring your ring light.")),
    ("I'm producing a film. In development.", "Has been 'in development' for nine years",
     "There might be a role for you behind the camera. Unpaid at first.", "unpaid weekends on a film that will never be made",
     ("Script read-through", "their flat", "Bring snacks, we'll be a while.")),
    ("Crypto founder.", "Runs a token nobody trades",
     "Get in early. I mean it. This is the ground floor.", "a chance to lose your savings",
     ("Token launch party", "a rented yacht that stays docked", "Wallets ready!")),
    ("I'm a life coach. Mindset, mostly.", "Self-certified last month",
     "You've got blocks. I can see it. First session's half price.", "an invoice",
     ("Masterclass: Manifesting Abundance", "a hotel conference room", "Life-changing. Early-bird pricing ends tonight.")),
    ("I run a networking collective.", "Runs a WhatsApp group",
     "We're like this party, but better. And more often.", "more parties like this one, minus the interesting people",
     ("Networking about networking", "a sports bar", "Bring 50 business cards.")),
    ("I'm launching a startup. Stealth mode.", "Has a domain name and a logo",
     "Need a co-founder. Equity only. Could be you.", "months of unpaid work for 0.5% of nothing",
     ("Hackathon (we'll build my idea)", "a co-working space", "Pizza provided. Probably.")),
    ("I consult. For various clients.", "Between jobs, creatively",
     "I could probably get you some work. Probably.", "vague promises",
     ("Business card exchange", "an airport hotel lobby", "Very strategic people.")),
    ("I'm an art dealer, sort of.", "Sells prints of their own paintings",
     "You should buy something now, before I'm famous.", "a sales pitch",
     ("My solo show", "a hair salon", "Prices go up after Friday.")),
    ("Motivational speaker.", "Spoke once, at a wedding",
     "Come to my talk. It'll change how you see yourself.", "a ticket to their talk",
     ("Unleash Your Inner CEO", "a community centre", "Only €25 at the door.")),
]

CLUELESS_ROLES = [
    ("I'm just the plus-one, honestly.", "Plus-one of someone who already left",
     "No idea who most of these people are, to be honest.", "nothing, though they mean well",
     ("Birthday drinks", "a pub", "Come along, it'll be fun!")),
    ("I'm a student too!", "Student, as lost as you are",
     "Do you know who the important people are? I was hoping you did.", "commiseration",
     ("Study group", "the library", "We could revise together.")),
    ("I do IT for the caterer.", "Off-duty IT technician",
     "Free wine, though, right?", "nothing for your career",
     ("Five-a-side football", "the park", "We're always one short.")),
    ("Came for the drinks, to be honest.", "Gatecrasher",
     "Have you tried the little salmon things? Amazing.", "canapé recommendations",
     ("Pub quiz", "a local pub", "Our team needs someone for geography.")),
    ("Accounts, at a company you won't have heard of.", "Accounts clerk",
     "It's very stable work. Very, very stable.", "a description of spreadsheets",
     ("Book club", "a neighbour's living room", "We're reading something long.")),
    ("I'm retired. My nephew dragged me here.", "Retired, charming, uninvolved",
     "In my day these parties had a band.", "stories about the old days",
     ("Bridge evening", "the retirement club", "We need a fourth.")),
    ("I'm a friend of the photographer.", "Friend of the hired photographer",
     "I mostly just hold the spare lenses.", "nothing",
     ("My cousin's band gig", "a youth club", "They're getting better!")),
    ("I sell insurance.", "Insurance salesperson, off the clock",
     "If you ever need cover, I'm your person. Otherwise...", "an insurance quote",
     ("Office karaoke night", "a karaoke bar", "We need fresh voices.")),
    ("I think I'm at the wrong party.", "Genuinely at the wrong party",
     "Is this not the dentists' reunion?", "directions to the dentists' reunion",
     ("Dentists' reunion", "a hotel two streets away", "If I ever find it.")),
    ("Yoga teacher. Well, training to be.", "Yoga trainee",
     "This room has such a weird energy, doesn't it?", "a free trial class",
     ("Sunrise yoga", "the beach", "6 a.m. sharp!")),
]

SMALL_TALK = {
    INTERESTING: [
        "They shake your hand firmly and ask what you're studying — and seem to actually listen.",
        "They give you a measured look, then a small smile. \"You're not one of the usual faces.\"",
        "They're polite but brief; you sense you have a few minutes, no more.",
        "They're mid-sentence with someone else, but turn to include you.",
    ],
    USELESS: [
        "They grab your hand with both of theirs. \"Love the energy! What's your story?\"",
        "They start talking before you've finished saying hello.",
        "They look over your shoulder twice while greeting you, then commit with enthusiasm.",
        "\"Ah, a student! I LOVE students. So hungry. So driven.\"",
    ],
    CLUELESS: [
        "They look relieved someone came over.",
        "They offer you a canapé from a napkin they've been saving.",
        "\"Oh, hi! Sorry, do we know each other?\"",
        "They smile warmly and ask if you know where the toilets are.",
    ],
}


@dataclass
class Person:
    pid: int
    name: str
    kind: str
    appearance: str
    details: str
    claim: str
    real_role: str
    substance: str
    offer: str
    small_talk: str
    event: Optional[Event]
    leaves_at: int  # minute of the cocktail at which they leave
    stage: int = 0  # how far the conversation has progressed (see cocktail.py)
    gave_card: bool = False
    gave_invite: bool = False

    @property
    def is_useful(self):
        return self.kind == INTERESTING

    def label(self):
        """How the person appears in the room list: by name once met, by looks before."""
        if self.stage > 0:
            return f"{self.name} — {self.appearance}"
        return self.appearance


def _pick(rng, pool, kind):
    idx = {INTERESTING: 1, CLUELESS: 2, USELESS: 3}[kind]
    return rng.choices([p[0] for p in pool], weights=[p[idx] for p in pool])[0]


def _article(word):
    return "an" if word[0] in "aeiou" else "a"


def make_person(rng, pid, name, kind, role):
    claim, real_role, substance, offer, (title, venue, pitch) = role
    age = _pick(rng, AGES, kind)
    figure = _pick(rng, FIGURES, kind)
    outfit = _pick(rng, OUTFITS, kind)
    behaviour = _pick(rng, BEHAVIOURS, kind)
    accessory = _pick(rng, ACCESSORIES, kind)
    appearance = f"{_article(age)} {age} {figure} in {outfit}, {behaviour}"
    details = f"Looking closer: {_article(age)} {age} {figure} in {outfit}, with {accessory}. Right now they are {behaviour}."

    # Interesting people are busy: they tend to leave early. Others may linger past the end.
    if kind == INTERESTING:
        leaves_at = rng.randint(20, 100)
    else:
        leaves_at = rng.randint(25, 140)

    event = Event(title=title, venue=venue, day=rng.randint(2, 21), host=name, pitch=pitch,
                  worthwhile=(kind == INTERESTING))
    return Person(pid=pid, name=name, kind=kind, appearance=appearance, details=details,
                  claim=claim, real_role=real_role, substance=substance, offer=offer,
                  small_talk=rng.choice(SMALL_TALK[kind]), event=event, leaves_at=leaves_at)


def generate_guests(rng=None, total=100, interesting=20, useless_share=0.5):
    """Generate `total` guests, `interesting` of whom are worth knowing."""
    rng = rng or random.Random()
    if interesting > len(INTERESTING_ROLES):
        raise ValueError(f"at most {len(INTERESTING_ROLES)} interesting guests are defined")
    names = set()
    while len(names) < total:
        names.add(f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}")
    names = list(names)
    rng.shuffle(names)

    schmucks = total - interesting
    n_useless = round(schmucks * useless_share)
    kinds = [INTERESTING] * interesting + [USELESS] * n_useless + [CLUELESS] * (schmucks - n_useless)
    rng.shuffle(kinds)

    interesting_roles = rng.sample(INTERESTING_ROLES, interesting)
    guests = []
    for pid, (name, kind) in enumerate(zip(names, kinds), start=1):
        if kind == INTERESTING:
            role = interesting_roles.pop()
        elif kind == USELESS:
            role = rng.choice(USELESS_ROLES)
        else:
            role = rng.choice(CLUELESS_ROLES)
        guests.append(make_person(rng, pid, name, kind, role))
    return guests
