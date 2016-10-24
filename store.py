from word import Word
from concept import Concept
from relation import Relation
from typing import Any, Iterable


class Store:

    def __init__(self, parent: 'Store'=None, label: str=None):
        self._words = {}  # type: dict[str, Word]
        self._concepts = {}  # type: dict[str, Concept]
        self._parent = parent
        self.label = label

    def get_word(self, word:str) -> Word:
        if self._parent is not None:
            w = self._parent.get_word(word)
            if w is not None:
                return w

        if word in self._words:
            return self._words[word]

        return None

    def define_or_get_word(self, word:str) -> Word:
        w = self.get_word(word)
        if w is None:
            w = Word(word)
            self._words[word] = w
        return w

    def words(self) -> Iterable[Word]:
        for l, w in self._words.items():
            yield w

    @staticmethod
    def key(concept: Any) -> str:
        if isinstance(concept, Concept):
            return concept.key()

        return str(concept)

    def add_concept(self, concept: Concept) -> None:
        key = Store.key(concept)
        self._concepts[key] = concept

    def get_concept(self, concept: Concept) -> Concept:
        if self._parent is not None:
            c = self._parent.get_concept(concept)
            if c is not None:
                return c

        key = Store.key(concept)
        if key in self._concepts:
            return self._concepts[key]
        return None

    def concepts(self) -> Iterable[Concept]:
        if self._parent is not None:
            for c in self._parent.concepts():
                yield c

        for l, c in self._concepts.items():
            yield c

    def own_concepts(self) -> Iterable[Concept]:
        for l, c in self._concepts.items():
            yield c

    def integrate(self, concept: Concept) -> Concept:
        integrated = self.get_concept(concept)
        if integrated is None:
            ip = []  # type: list[Concept]
            for p in concept.parents:
                ip.append(self.integrate(p))

            integrated = Concept(concept.name, concept.relation, ip, concept.probability)
            integrated.store = self
            integrated.register_with_parents()
            self.add_concept(integrated)

            if integrated.relation == Relation.Word:
                word = integrated.name
                if word not in self._words:
                    w = Word(word)
                    w.add_meaning(integrated)
                    self._words[word] = w
            elif integrated.relation == Relation.Implication:
                integrated.propagate_probability_from_parent(integrated.parents[0])

        else:
            integrated.merge_probability(concept.probability)

        return integrated
