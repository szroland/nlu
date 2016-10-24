from typing import Any
from concept import Concept
from store import Store
from relation import Relation


def node(node_id: Any, name: str, w: int, color: str, shape: str) -> str:
    s = "{ data: { id:'"+str(node_id) \
        + "', name:'"+name \
        + "', weight:"+str(w) \
        + ", faveColor:'"+color \
        + "', faveShape:'"+shape+"' } },"
    return s


def edge(source: Any, target: Any, label: str, color: str, strength: int) -> str:
    s = "{ data: {" \
        + "source: '"+str(source) \
        + "', target: '"+str(target)+"'"
    if label is not None:
        s += ", label: '"+label+"'"
    if color is not None:
        s += ", faveColor: '"+color+"'"
    if strength is not None:
        s += ", strength: "+str(strength)
    s += "} },"
    return s


def is_simple_2arg_concept(concept: Concept) -> bool:
    if concept.parents is None or len(concept.parents) != 2:
        return False

    if len(concept.children) > 0:
        return False

    return True


def graph(store: Store, words: bool=False, simplify: bool=True):
    s = "{ nodes: ["
    if words:
        for word in store.words():
            s += "\n"+node(id(word), word.word, 50, '#F5A45D', 'octagon')

    for concept in store.concepts():
        if concept.relation == Relation.Word:
            s += "\n"+node(id(concept), concept.name, 50, "#6FB1FC", 'ellipse')
        else:
            if not simplify or not is_simple_2arg_concept(concept):
                l = concept.name
                if l is None:
                    l = str(concept)
                s += "\n"+node(id(concept), l, 50, "#86B342", 'triangle')

    s += "], edges: ["

    if words:
        for word in store.words():
            for meaning in word.meanings():
                s += "\n"+edge(id(word), id(meaning), None, "#6FB1FC", 10)

    for concept in store.concepts():
        if simplify and is_simple_2arg_concept(concept):
            p = ''
            if concept.probability < 1.0:
                p = ' (p='+str(concept.probability)+')'

            s += "\n"+edge(
                id(concept.parents[0]), id(concept.parents[1]),
                concept.relation.name+p, "#EDA1ED", 50)
        else:
            for parent in concept.parents:
                s += "\n"+edge(id(concept), id(parent), None, "#EDA1ED", 50)

    s += "] }"
    return s
