import unittest
from concept import Concept
from text_parser import SpacyTranslator
from parser import parse
from typing import Iterable
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SpacyTranslatorTest(unittest.TestCase):

    parser = SpacyTranslator()

    def assert_same_concept(self, a: Concept, b: Concept) -> bool:
        self.assertEqual(a.name, b.name)
        self.assertEqual(a.relation.name, b.relation.name)
        self.assertEqual(a.parents is None, b.parents is None)
        self.assertEqual(len(a.parents), len(b.parents))

        for i in range(len(a.parents)):
            self.assert_same_concept(a.parents[i], b.parents[i])

    def expect_translation(self, input: str, output: Iterable[str]):
        m = self.parser.parse(input)
        for o in output:
            expected_concept = parse(o)
            try:
                actual_concept = next(m)
                logger.debug("Checking %s against %s" % (expected_concept, actual_concept))
                self.assert_same_concept(expected_concept, actual_concept)
            except StopIteration:
                self.fail(msg="No translation, expected %s" % expected_concept)

    def test_single_class_def(self):
        self.expect_translation(
            "Budapest is a city.",
            ["C(Budapest,city)"])

    def test_multiple_class_defs(self):
        self.expect_translation(
            "Budapest, Tokyo and Vienna are cities.",
            [
                "C(Budapest,city)",
                "C(Tokyo,city)",
                "C(Vienna,city)"
            ])

    def test_simple_feature(self):
        self.expect_translation(
            "Joe is sad. Peter is tired. Mary was stunned. I'm bored. You and I have been crazy for some time.",
            [
                "F(Joe, sad)",
                "F(Peter, tired)",
                "F(Mary, stunned)",
                "F(i, bored)",
                "F(you, crazy)",
                "F(i, crazy)"
            ]
        )

    def test_general_ability_statements(self):
        self.expect_translation(
            "Birds can fly. Dogs bark. Penguins swim a lot. Some cats eat fish. "
            "Small children fear the walking dead.",
            [
                "F(bird,fly)",
                "F(dog,bark)",
                "F(penguin,swim)",
                "F(cat,eat)",
                "F(child,fear)",
            ]
        )

    def test_simple_implications(self):
        self.expect_translation(
            "If a person is tired, that person will be slow.",
            [
                "IM(F(person,tired),F(person,slow))"
            ]
        )

    def test_direct_feature_question(self):
        self.expect_translation(
            "Is Joe tired? Is Joe a bird?",
            [
                "F(Joe, tired)",
                "C(Joe, bird)"
            ]
        )

    def test_generic_feature_question(self):
        self.expect_translation(
            "Who is Joe? What is Joe? What is Joe like?",
            [
                "C(Joe, ?)",
                "C(Joe, ?)",
                "F(Joe, ?)",
            ]
        )

    def test_simple_action(self):
        self.expect_translation(
            "Joe is running. If you run, you will be tired. Will Joe be tired?",
            [
                "A(Joe, run)",
                "IM(A(you, run), F(you, tired))",
                "F(Joe, tired)"
            ]
        )

    def test_more_complex_statements(self):
        self.expect_translation(
            "She arrived yesterday from Budapest to Vienna. She stayed at the Hilton on the Ring.",
            [
                "F(A(she, arrive), T(yesterday), R(from, Budapest), R(to, Vienna))",
                "F(A(she, stay), R(at, Hilton), R(on, ring))"
            ]
        )

    def test_action_questions(self):
        self.expect_translation(
            "From where did she arrive? Where did she arrive from? Where did she stay? When did she arrive?",
            [
                "F(A(she,arrive),R(from,?))",
                "F(A(she,arrive),R(from,?))",
                "F(A(she,stay),R(?,?))",
                "F(A(she,arrive),T(?))"
            ]
        )

    def test_possession(self):
        self.expect_translation(
            "Bob is Mary's brother. You are my friend. Who is Mary's cousin? Whose brother is Tom?",
            [
                "D(Bob, P(Mary, brother))",
                "D(you, P(my, friend))",
                "D(?, P(Mary, cousin))",
                "D(Tom, P(?, brother))"
            ]
        )

if __name__ == '__main__':
    unittest.main()
