from concept import Concept
from typing import Iterable


class Word:

    def __init__(self, word: str, parent: 'Word'=None):
        self.word = word
        self._parent = parent
        self._meaning = []  # type: list[Concept]

    def add_meaning(self, concept: Concept) -> None:
        self._meaning.append(concept)

    def meanings(self) -> Iterable[Concept]:
        if self._parent is not None:
            for m in self._parent.meanings():
                yield m

        for m in self._meaning:
            yield m
