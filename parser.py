from concept import Concept
from store import Store
from relation import Relation


def is_word(expression: str) -> bool:
    s = expression.find('(')
    e = expression.find(')')
    return s < 0 or e < s


def parse(expression: str, store: Store=None, label: str=None, probability: float=1.0):
    if is_word(expression):
        word = None
        if store is not None:
            word = store.get_word(expression)
        if word is not None:
            return next(word.meanings())

        if label is None:
            label = expression

        return Concept.word(label)
    else:
        return parse_compound_concept(expression, store, label, probability=probability)


def parse_compound_concept(expression: str, store: Store, label: str=None, probability: float=1.0):
    s = expression.find('(')
    e = expression.rfind(')')

    rel = Relation.find(expression[:s])

    args = []  # type: list[str]
    d = 0
    arg_start = s+1
    for x in range(s+1, e):
        c = expression[x]
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        elif c == ',':
            if d == 0:
                args.append(expression[arg_start:x])
                arg_start = x+1

    args.append(expression[arg_start:e])
    arg_concepts = []  # type: list[Concept]
    arg_probability = probability
    if rel == Relation.Implication:
        arg_probability = .5

    for a in args:
        arg = parse(a.strip(), store, probability=arg_probability)
        arg_concepts.append(arg)

    if label is None and e < len(expression)-1:
        label = expression[e+1:].strip()

    return Concept(label, rel, arg_concepts, probability=probability)
