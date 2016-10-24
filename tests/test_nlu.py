import unittest
from nlu import NLU
from graph import graph

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class NLUTestCase(unittest.TestCase):

    def test_trivial_match(self):
        nlu = NLU()
        nlu.integrate("C(Budapest, city)")
        q, a, c = nlu.ask("C(Budapest, ?)")
        logger.info("Answer to question %s: %s" % (q, nlu.create_answer(q, a)))

        self.assertIsNotNone(a)
        self.assertEqual(set(map(lambda x: x.name, a.values())), {'city'})

    def test_class_deduction(self):
        nlu = NLU()
        nlu.integrate("C(Bp,city)")
        nlu.integrate("C(city,place)")

        q, a, c = nlu.ask("C(Bp, place)")
        logger.info("Answer to question %s: %s" % (q, nlu.create_answer(q, a)))
        self.assertIsNotNone(a)

    def test_class_other_relations(self):
        nlu = NLU()
        nlu.integrate("F(bird,fly)")
        nlu.integrate("C(penguin,bird)")
        nlu.integrate("F(penguin,swim)")

        q, a, c = nlu.ask("F(penguin, fly)")
        logger.info("State:\n%s\n" % graph(nlu.question_store))
        logger.info("Answer to question %s: %s" % (q, nlu.create_answer(q, a)))
        self.assertIsNotNone(a)

    def test_integrate_defines_probability(self):
        nlu = NLU()
        nlu.integrate("IM(F(Joe,tired),F(Joe,slow))")
        q, a, c = nlu.ask("F(Joe,tired)")
        self.assertEqual(c.probability, .5)

        nlu.integrate("F(Joe,tired)")
        q, a, c = nlu.ask("F(Joe,tired)")
        self.assertIsNotNone(c)
        self.assertEqual(c.probability, 1.0)

    def test_implication_transfers_probability(self):
        nlu = NLU()
        nlu.integrate("IM(F(Joe,tired),F(Joe,slow))")
        nlu.integrate("IM(F(Joe,slow),F(Joe,angry))")
        nlu.integrate("F(Joe,tired)")

        q, a, c = nlu.ask("F(Joe,angry)")
        self.assertIsNotNone(c)
        self.assertEqual(c.probability, 1.0)

    def test_implication_works_after_parent_statement(self):
        nlu = NLU()
        nlu.integrate("F(Joe,tired)")
        nlu.integrate("IM(F(Joe,tired),F(Joe,slow))")
        nlu.integrate("IM(F(Joe,slow),F(Joe,angry))")

        q, a, c = nlu.ask("F(Joe,angry)")
        self.assertIsNotNone(c)
        self.assertEqual(c.probability, 1.0)

    def test_implication_with_class(self):
        nlu = NLU()
        nlu.integrate("IM(F(person,tired),F(person,slow))")
        nlu.integrate("IM(F(person,slow),F(person,angry))")
        nlu.integrate("C(Joe,person)")
        nlu.integrate("F(Joe,tired)")

        logger.info("State:\n%s\n" % graph(nlu.working_memory))
        q, a, c = nlu.ask("F(Joe,angry)")

        logger.info("State:\n%s\n" % graph(nlu.question_store))
        self.assertIsNotNone(c)
        self.assertEqual(c.probability, 1.0)


if __name__ == '__main__':
    unittest.main()
