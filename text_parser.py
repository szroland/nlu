import spacy
import time
from concept import Concept
from typing import Iterable
from relation import Relation

import logging
logger = logging.getLogger(__name__)


class TextToMentalase:
    def parse(self, text:str) -> Iterable[Concept]:
        pass


__spacy_parsers = {}


def get_spacy_parser(language='en'):
    if language in __spacy_parsers:
        return __spacy_parsers[language]
    logger.warn("Loading text parsers for language '%s' (this may take a while...)" % language)
    start = time.time()
    result = spacy.load(language)
    end = time.time()
    logger.warn('Models loaded, took %r seconds' % (end-start))
    __spacy_parsers[language] = result
    return result


class SpacyTranslator(TextToMentalase):

    def __init__(self, language='en', nlp=None):
        self.language = language;
        self.__nlp = nlp

    @property
    def nlp(self):
        if self.__nlp is None:
            self.__nlp = get_spacy_parser(self.language)
        return self.__nlp

    def dep(self, root, type):
        if root is None:
            return None
        for c in root.children:
            if c.dep_ == type:
                return c
        return None

    def deps(self, root, type):
        if root is None:
            return None
        for c in root.children:
            if c.dep_ == type:
                yield c

    def subj(self, sentence) -> Iterable:
        s = self.dep(sentence, 'nsubj')
        while s is not None:
            yield s

            s = self.dep(s, 'conj')

    @staticmethod
    def name(noun):
        if noun.pos_ == 'PROPN':  # keep case for proper nouns
            return noun.orth_
        if noun.tag_ == 'WP':  # replace WH-pronouns with ?
            return '?'
        if noun.tag_ == 'WRB':
            return '?'
        return noun.lemma_

    def parse_simple(self, root) -> Iterable:
        if root.lemma_ == 'be':
            attr = self.dep(root, 'attr')
            if attr and attr.pos_ == 'NOUN':
                rel = Relation.Class
                prep = self.dep(root, 'prep')
                if prep is not None and prep.lemma_ == 'like':
                    rel = Relation.Feature
                for subj in self.subj(root):
                    yield Concept(None, rel, [
                        Concept(self.name(subj), Relation.Word, []),
                        Concept(self.name(attr), Relation.Word, [])
                    ])
            acomp = self.dep(root, 'acomp')
            if acomp and acomp.pos_ == 'ADJ':
                for subj in self.subj(root):
                    yield Concept(None, Relation.Feature, [
                        Concept(self.name(subj), Relation.Word, []),
                        Concept(self.name(acomp), Relation.Word, [])
                    ])
        elif root.pos_ == 'VERB':
            for subj in self.subj(root):
                rel = Relation.Feature
                aux = self.dep(root, 'aux')
                mark = self.dep(root, 'mark')
                if aux is not None and aux.lemma_ == 'be':  # continuous
                    rel = Relation.Action
                if aux is not None and aux.lemma_ == 'do' and aux.tag_ == 'VBD':  # past tense with aux do
                    rel = Relation.Action
                if root.tag_ == 'VBD':  # past tense
                    rel = Relation.Action
                if mark is not None and mark.lemma_ == 'if':  # conditional
                    rel = Relation.Action

                concept = Concept(None, rel, [
                    Concept.word(self.name(subj)),
                    Concept.word(self.name(root))
                ])

                features = []
                npadvmod = self.dep(root, 'npadvmod')
                if npadvmod is not None:
                    features.append(Concept(None, Relation.Time, [
                        Concept.word(self.name(npadvmod))
                    ]))

                advmod = self.dep(root, 'advmod')
                if advmod is not None:
                    if advmod.lemma_ == 'where':
                        features.append(Concept(None, Relation.Relative, [Concept.word('?'), Concept.word('?')]))
                    if advmod.lemma_ == 'when':
                        features.append(Concept(None, Relation.Time, [Concept.word('?')]))

                for prep in self.deps(root, 'prep'):
                    while prep is not None:
                        obj = self.dep(prep, 'pobj')
                        obj_name = '?'
                        if obj is not None:
                            obj_name = self.name(obj)

                        features.append(Concept(None, Relation.Relative, [
                            Concept.word(self.name(prep)),
                            Concept.word(obj_name)
                        ]))
                        prep = self.dep(prep, 'prep')

                if len(features) > 0:
                    concept = Concept(None, Relation.Feature, [
                        concept
                    ] + features)

                yield concept

    def parse_sentence(self, root) -> Iterable:
        advcl = self.dep(root, 'advcl')
        mark = self.dep(advcl, 'mark')
        if advcl and mark and mark.lemma_ == 'if':
            condition = next(self.parse_simple(advcl))
            for action in self.parse_simple(root):
                yield Concept(None, Relation.Implication, [
                    condition, action
                ])

        else:
            for c in self.parse_simple(root):
                yield c

    def dump_sentence(self, token, indent="  "):
        logger.debug("%s%s (%s %s %s)" % (indent, token.lemma_, token.pos_, token.tag_, token.dep_))
        for child in token.children:
            self.dump_sentence(child, indent + "  ")

    def parse(self, text: str):
        doc = self.nlp(text)
        for sentence in doc.sents:
            logger.debug('Parsing: %r ROOT: %s (%s)' % (sentence, sentence.root, sentence.root.lemma_))
            self.dump_sentence(sentence.root)
            for concept in self.parse_sentence(sentence.root):
                yield concept

    def explore(self, text):
        doc = self.nlp(text)
        logger.info('Doc %r' % doc)
        for sentence in doc.sents:
            logger.debug(' - Sentence: %r ROOT: %s (%s)' % (sentence, sentence.root, sentence.root.lemma_))
            self.parse_sentence(sentence.root)
            # for e in sentence.subtree:
            #   logger.debug('   - %r' % e)
        for token in doc:
            logger.debug(' - Token: %r: %s %s %s (shape=%s, entity=%s, lemma=%s, head=%s)' %
                         (token, token.pos_, token.tag_, token.dep_,
                          token.shape_, token.ent_type_, token.lemma_, token.head))
        return doc

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = SpacyTranslator()
    parser.explore(
        "If Joe is tired, Joe becomes slow. "
        "If Joe is slow, Joe becomes angry. "
        "Joe is tired. "
        "Is Joe angry?"
    )
    parser.explore(
        "Budapest, Tokyo and Vienna are cities. "
        "She arrived yesterday from Vienna to Budapest. "
        "She stayed at the Hilton on the Ring."
        "She only had 2 bags and a backpack and $100 in her valet"
    )
