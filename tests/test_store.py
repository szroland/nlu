import unittest
from store import Store
from concept import Concept
from relation import Relation
from parser import parse

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class StoreTestCase(unittest.TestCase):

    def test_concept_storing(self):
        s = Store()
        s.add_concept(1)
        s.add_concept(2)

        l = set(s.concepts())

        self.assertEqual(l, {1, 2})

    def test_uses_words_in_parent(self):
        parent = Store()
        child = Store(parent)

        parent.define_or_get_word('parent')
        self.assertIsNotNone(child.get_word('parent'))

    def test_uses_concepts_in_parent(self):
        parent = Store()
        child = Store(parent)

        raw = Concept(None, Relation.Class, [Concept.word('c1'), Concept.word('c2')])
        in_parent = parent.integrate(raw)
        in_child = child.integrate(raw)

        self.assertEqual(id(in_parent), id(in_child))

    def test_concept_iterator_includes_parent_concepts(self):
        parent = Store()
        child = Store(parent)

        parent.add_concept(Concept.word("p"))
        child.add_concept(Concept.word("c"))

        l = set(map(lambda c: c.name, child.concepts()))
        self.assertEqual(l, {"p", "c"})

    def test_integrate_is_recursive(self):

        store = Store()
        store.integrate(parse("C(A,B)"))

        self.assertIsNotNone(store.get_concept(parse("A")))

    def test_parse_interference_with_child_links(self):
        store = Store()
        # F links to person and slow
        store.integrate(parse("F(person,slow)"))

        # this should not link itself to the integrated "slow" concept
        parse("F(person,slow)", store)

        integrated = store.get_concept(parse("slow"))
        self.assertEqual(len(integrated.children), 1)

if __name__ == '__main__':
    unittest.main()
