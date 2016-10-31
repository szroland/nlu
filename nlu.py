from concept import Concept
from store import Store
from generator import InheritFromParentClass
from typing import Mapping, Optional, List
from parser import parse
from graph import graph
from text_parser import SpacyTranslator

import logging
logger = logging.getLogger(__name__)

class NLU:

    def __init__(self):
        self.working_memory = Store(label='WM')
        self.question_store = Store(self.working_memory, label='Question')
        self.concepts = []  # type: list[Concept]
        self.text_parser = SpacyTranslator()

    def is_mentalase(self, expression: str):
        if '(' in expression and ')' in expression:
            return True
        if ' ' in expression:
            return False

        #single word
        return True

    def integrate(self, expression: str, label: str=None, probability: float=1.0) -> List[Concept]:
        # for now, only reset question_store when new statements are integrated into the working memory
        self.question_store = Store(self.working_memory, label='Question')

        parsed = []
        if self.is_mentalase(expression):
            concept = parse(expression, self.working_memory, label, probability)
            parsed.append(concept)
            self.working_memory.integrate(concept)
        else:
            for concept in self.text_parser.parse(expression):
                parsed.append(concept)
                self.working_memory.integrate(concept)
        return parsed

    def ask(self, question: str) -> (Concept, Optional[Mapping[Concept, Concept]], Optional[Concept]):

        if self.is_mentalase(question):
            q = parse(question, self.question_store)  # type: Concept
        else:
            q = next(self.text_parser.parse(question))

        for concept in self.working_memory.concepts():  # type: Concept
            match = concept.matches(q)
            if match is not None:
                return q, match, concept

        # todo: handle available generators in a more generic way
        generator = InheritFromParentClass()
        for concept in generator.gen(self.question_store):  # type: Concept
            match = concept.matches(q)
            if match is not None and abs(concept.probability-0.5) > 0.0:
                return q, match, concept

        # another pass at all generated concepts to see if result was generated as part of larger compound concept
        # or, probability of result changed during generating concepts
        # todo: replace this with the ability to mark processed items in the store to be more efficient

        for concept in self.question_store.own_concepts():  # type: Concept
            match = concept.matches(q)
            if match is not None:
                return q, match, concept

        return q, None, None

    @staticmethod
    def create_answer(question: Concept, mapping: Mapping[Concept, Concept]) -> Concept:
        if mapping is None:
            return None

        # simple
        if question.is_simple():
            if question in mapping:
                return mapping[question]
            return question

        # compound
        ap = []  # type: list[Concept]
        for p in question.parents:
            ap.append(NLU.create_answer(p, mapping))

        return Concept(question.name, question.relation, ap)

    def ask_question(self, question: str):

        parsed, match, matched_concept = self.ask(question)
        answer = self.create_answer(parsed, match)
        print("Question: %s" % parsed)

        direct = str(answer)
        p = ''
        if matched_concept is not None:
            p = '(p=%r)' % matched_concept.probability
        print("Answer: %s %s" % (direct, p))

        if matched_concept is not None:
            full = str(matched_concept)
            if direct != full:
                print("Full answer: %s" % full)

if __name__ == '__main__':
    nlu = NLU()
    nlu.integrate("C(Budapest, city)")

    nlu.integrate("C(New York, city)")
    nlu.integrate("C(Tokyo, city)")
    nlu.integrate("C(city, location)")

    nlu.integrate("F(A(she,arrive),T(yesterday),R(from,Budapest),R(to,Vienna))", "She arrived y from Bp to V")
    nlu.integrate("F(A(she,stay),R(at,Hilton),R(on,Ring))", "She stayed at the Hilton")

    print(graph(nlu.working_memory, words=True))

    nlu.ask_question("?")
    nlu.ask_question("F(A(she,arrive), T(?))")
    nlu.ask_question("A(she,?)")
    nlu.ask_question("F(A(?,stay),R(at, Hilton))")
    nlu.ask_question("F(A(she,?),T(yesterday))")

    nlu.ask_question("F(?,T(?))")
