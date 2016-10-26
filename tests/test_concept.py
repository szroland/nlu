import unittest
from parser import parse
from store import Store

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ConceptTestCase(unittest.TestCase):

    def test_match_first_arg_is_special(self):
        s = Store()
        s.integrate(parse("joe"))
        s.integrate(parse("person"))

        c = parse("C(joe, person)", s)
        q = parse("C(person, ?)", s)

        mapping = c.matches(q)

        self.assertIsNone(mapping)

if __name__ == '__main__':
    unittest.main()
