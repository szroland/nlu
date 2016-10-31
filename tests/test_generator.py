import unittest
from nlu import NLU
from generator import InheritFromParentClass
from graph import graph

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class InheritFromParentClassTestCase(unittest.TestCase):

    def test_class_relationship_is_one_way(self):
        nlu = NLU()
        nlu.integrate("C(Mary, person)")
        nlu.integrate("C(Joe, person)")
        nlu.integrate("C(kid, person)")

        logger.info("State: \n%s\n" % graph(nlu.working_memory))

        gen = InheritFromParentClass()
        concepts = list(gen.gen(nlu.question_store))

        logger.info("Generated concepts: %r" % concepts)

        self.assertEqual(len(concepts), 0)

    def test_class_relationship_is_one_way_2(self):
        nlu = NLU()
        nlu.integrate("C(Mary, person)")
        nlu.integrate("C(Joe, person)")
        nlu.integrate("C(kid, person)")

        nlu.integrate("C(person, entity)")
        nlu.integrate("C(firm, entity)")

        logger.info("State: \n%s\n" % graph(nlu.working_memory))

        gen = InheritFromParentClass()
        concepts = list(gen.gen(nlu.question_store))
        logger.info("Step 1: Generated concepts: %r" % concepts)
        # should generate Class for Mary, Joe, kid -> entity
        for gc in concepts:
            self.assertEqual(gc.parents[1].name, 'entity')

        concepts = list(gen.gen(nlu.question_store))
        logger.info("Step 2: Generated concepts: %r" % concepts)
        # nothing else should be generated
        self.assertEqual(len(concepts), 0)


if __name__ == '__main__':
    unittest.main()
