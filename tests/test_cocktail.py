import random
import unittest

from junket.cocktail import Cocktail, APPROACH_COST, TALK_COST, DURATION
from junket.people import INTERESTING, CLUELESS, USELESS, generate_guests


def first(game, kind):
    return next(g for g in game.present() if g.kind == kind and g.leaves_at > DURATION)


class GuestsTest(unittest.TestCase):
    def test_room_has_100_guests_20_interesting(self):
        guests = generate_guests(random.Random(3))
        self.assertEqual(len(guests), 100)
        self.assertEqual(sum(g.kind == INTERESTING for g in guests), 20)
        self.assertEqual(len({g.name for g in guests}), 100)

    def test_seed_is_reproducible(self):
        a = [g.appearance for g in generate_guests(random.Random(7))]
        b = [g.appearance for g in generate_guests(random.Random(7))]
        self.assertEqual(a, b)


class CocktailTest(unittest.TestCase):
    def setUp(self):
        self.game = Cocktail(seed=42)

    def test_names_hidden_until_approached(self):
        g = self.game.guests[0]
        self.assertNotIn(g.name, self.game.room())
        self.game.do(f"approach {g.pid}")
        self.assertIn(g.name, self.game.room())

    def test_actions_cost_time(self):
        g = first(self.game, CLUELESS)
        self.game.do(f"approach {g.pid}")
        self.assertEqual(self.game.minute, APPROACH_COST)
        self.game.do("talk")
        self.assertEqual(self.game.minute, APPROACH_COST + TALK_COST)
        self.game.do("room")
        self.game.do("agenda")
        self.assertEqual(self.game.minute, APPROACH_COST + TALK_COST)

    def test_interesting_person_gives_card_then_worthwhile_invite(self):
        g = first(self.game, INTERESTING)
        self.game.do(f"approach {g.pid}")
        self.game.do("talk")
        self.assertEqual(len(self.game.contacts), 0)
        self.game.do("talk")
        self.assertEqual(self.game.contacts.contacts[0].occupation, g.real_role)
        self.game.do("talk")
        self.assertTrue(self.game.agenda.events[0].worthwhile)

    def test_useless_person_is_pushy_with_pointless_event(self):
        g = first(self.game, USELESS)
        self.game.do(f"approach {g.pid}")
        self.game.do("talk")
        self.assertEqual(len(self.game.contacts), 1)
        self.game.do("talk")
        self.assertEqual(len(self.game.agenda), 1)
        self.assertFalse(self.game.agenda.events[0].worthwhile)

    def test_cocktail_ends_after_60_minutes(self):
        g = first(self.game, CLUELESS)
        self.game.do(f"approach {g.pid}")
        while not self.game.over:
            out = self.game.do("talk")
            if "enough time" in out:
                break
        self.assertLessEqual(self.game.minute, DURATION)
        self.assertGreaterEqual(self.game.minute, DURATION - TALK_COST + 1)

    def test_guests_leave_over_time(self):
        before = len(self.game.present())
        self.game.minute = 0
        self.game._advance(DURATION)
        self.assertLess(len(self.game.present()), before)
        self.assertTrue(self.game.over)
        self.assertIn("already left", self.game.do(f"approach {next(iter(self.game._left))}"))

    def test_bad_input(self):
        self.assertIn("Which guest", self.game.do("approach bob"))
        self.assertIn("no guest", self.game.do("approach 999"))
        self.assertIn("not talking", self.game.do("talk"))
        self.assertIn("Unknown", self.game.do("dance"))


if __name__ == "__main__":
    unittest.main()
