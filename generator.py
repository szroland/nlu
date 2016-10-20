from store import Store
from relation import Relation
from concept import Concept

from typing import Iterable


def clone_concept_with_replacing_parent(concept: Concept, old_parent: Concept, new_parent: Concept) -> Concept:
    np = []  # type: list(Concept)
    for p in concept.parents:
        if p == old_parent:
            np.append(new_parent)
        else:
            np.append(p)

    return Concept(concept.name, concept.relation, np, concept.probability)


class InheritFromParentClass:

    def gen(self, store: Store) -> Iterable[Concept]:

        keep_searching = True
        while keep_searching:
            keep_searching = False

            # todo: do not explicitly list() items (need to handle concurrent store modifications)
            classes = list(filter(lambda c: c.relation == Relation.Class, store.concepts()))

            for class_concept in classes:  # type: Concept
                source, target = class_concept.parents
                target_children = list(target.children)

                for tc in target_children:  # type: Concept
                    if tc == class_concept:
                        continue

                    inherited = clone_concept_with_replacing_parent(tc, target, source)

                    if store.get_concept(inherited) is None:
                        keep_searching = True
                        yield store.integrate(inherited)
