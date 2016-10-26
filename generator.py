from store import Store
from relation import Relation
from concept import Concept

from typing import Iterable, Set, Mapping
from queue import Queue

import logging
logger = logging.getLogger(__name__)


def clone_concept_with_replacing_parent(concept: Concept, mapping: Mapping[Concept, Concept],
                                        old_parent: Concept, new_parent: Concept) -> (Concept, bool):
    if concept in mapping:
        return mapping[concept], True

    np = []  # type: list(Concept)
    replaced = False
    for p in concept.parents:
        if p == old_parent:
            np.append(new_parent)
            replaced = True
        else:
            clone, flag = clone_concept_with_replacing_parent(p, mapping, old_parent, new_parent);
            np.append(clone)
            if flag:
                replaced = True

    result = Concept(concept.name, concept.relation, np, concept.probability)
    if replaced:
        mapping[concept] = result
    return result, replaced


def collect_children(concept: Concept) -> Set[Concept]:
    result = set()
    pending = Queue()
    pending.put(concept)
    while not pending.empty():
        c = pending.get()  # type: Concept
        result.add(c)
        for child in c.children:  # type: Concept
            # for C, only include the relationship if this is the source
            # todo: this may apply to other relationship types as well

            if child.relation == Relation.Class and child.parents[0] != c:
                continue

            pending.put(child)
    return result


class InheritFromParentClass:

    def gen(self, store: Store) -> Iterable[Concept]:

        keep_searching = True
        while keep_searching:
            keep_searching = False

            # todo: do not explicitly list() items (need to handle concurrent store modifications)
            classes = list(filter(lambda c: c.relation == Relation.Class, store.concepts()))

            for class_concept in classes:  # type: Concept
                source = class_concept.parents[0]
                target = class_concept.parents[1]
                logger.debug("Using class concept %s" % class_concept)
                target_children = collect_children(target)

                mapping = {}
                for tc in target_children:  # type: Concept
                    clone_concept_with_replacing_parent(tc, mapping, target, source)

                for template, clone in mapping.items():
                    if store.get_concept(clone) is None:
                        keep_searching = True
                        logger.debug("Generated concept %s" % clone)
                        yield store.integrate(clone)

