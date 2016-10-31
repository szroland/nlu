from typing import List, Set, Mapping
from relation import Relation


def merge_probability(p1:float, p2:float) -> float:
    d1 = abs(p1 - .5)
    d2 = abs(p2 - .5)
    if d1 > d2:
        return p1
    return p2


class Concept:

    def __init__(self, name: str, relation: Relation, parents: List['Concept'], probability: float=1.0):

        self.name = name
        self.relation = relation
        self.parents = parents  # type: List[Concept]
        self.probability = probability

        if relation == Relation.Word:
            self._key = name
        else:
            self._key = relation.id + '(' + ','.join(map(Concept.key, parents)) + ')'

        self.children = set()  # type: Set[Concept]
        self.store = None  # type: Store


    def __repr__(self):
        return "Concept(name=%r,relation=%r,parents=%r,p=%r)" % \
               (self.name, self.relation, self.parents, self.probability)

    def __str__(self):
        if self.relation == Relation.Word:
            ret = self.name
        else:
            ret = self.relation.name + '(' + ','.join(map(str, self.parents)) + ')'

        if self.probability < 1.0:
            ret += ' (p='+str(self.probability)+')'
        return ret

    def set_probability(self, value:float) -> None:
        if self.probability != value:
            self.probability = value
            for c in self.children:  # type: Concept
                c.propagate_probability_from_parent(self)

    def merge_probability(self, value:float) -> None:
        self.set_probability(merge_probability(self.probability, value))

    def propagate_probability_from_parent(self, parent: 'Concept') -> None:
        if self.relation == Relation.Implication:
            if len(self.parents) == 2 and parent == self.parents[0]:
                self.parents[1].merge_probability(parent.probability)

    def key(self):
        return self._key

    def add_child(self, child: 'Concept') -> None:
        self.children.add(child)

    def register_with_parents(self) -> None:
        for p in self.parents:
            p.add_child(self)

    @staticmethod
    def word(label: str) -> 'Concept':
        return Concept(label, Relation.Word, [])

    def is_question(self) -> bool:
        if self.name == '?':
            return True

        if self.parents is not None:
            for p in self.parents:  # type: Concept
                if p.is_question():
                    return True

        return False

    def is_simple(self) -> bool:
        return self.parents is None or len(self.parents) == 0

    def has_parent(self, concept: 'Concept') -> bool:
        for p in self.parents:
            if p == concept:
                return True

        return False

    @staticmethod
    def match_and_remove(concept: 'Concept', remaining: List['Concept']) -> Mapping['Concept', 'Concept']:
        for i in range(len(remaining)):
            mapping = remaining[i].matches(concept)
            if mapping is not None:
                del remaining[i]
                return mapping

        return None

    def matches(self, pattern: 'Concept') -> Mapping['Concept', 'Concept']:
        if pattern.is_simple() and pattern.is_question():
            return {pattern: self}

        if pattern.relation != self.relation:
            return None

        # simple concept
        if pattern.is_simple():
            if self == pattern:
                return {}
            elif self.is_simple() and self.name == pattern.name:
                return {}
            else:
                return None

        if self.is_simple():
            return None

        # compound concept
        mapping = {}  # type: dict[Concept, Concept]

        # first arg is special and fixed
        # todo: is this based on relation type?
        match = self.parents[0].matches(pattern.parents[0])
        if match is None:
            return None
        mapping.update(match)

        # now match the rest of args unordered
        remaining = list(self.parents[1:])
        questions = []  # type: List[Concept]

        # match fixed parents first
        for p in pattern.parents[1:]:
            if p.is_question():
                questions.append(p)
            else:
                if Concept.match_and_remove(p, remaining) is None:
                    return None

        # match questions
        for q in questions:
            # todo: consider all placeholders instead of simple eager matching
            match = Concept.match_and_remove(q, remaining)
            if match is None:
                return None
            mapping.update(match)

        return mapping
