# -*- coding: utf-8 -*-
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.schema.interfaces import ITokenizedTerm
from zope.schema.interfaces import IVocabulary


@implementer(ISerializeToJson)
@adapter(IVocabulary, Interface)
class SerializeVocabularyToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, vocabulary_id):
        vocabulary = self.context
        query = self.request.form.get('q', '')

        terms = []
        for term in vocabulary:
            if query.lower() not in term.title.lower():
                continue
            terms.append(term)

        batch = HypermediaBatch(self.request, terms)

        serialized_terms = []
        for term in batch:
            serializer = getMultiAdapter((term, self.request),
                                         interface=ISerializeToJson)
            serialized_terms.append(serializer())

        result = {
            '@id': batch.canonical_url,
            'terms': serialized_terms,
            'terms_total': batch.items_total,
        }
        links = batch.links
        if links:
            result['batching'] = links
        return result


@implementer(ISerializeToJson)
@adapter(ITokenizedTerm, Interface)
class SerializeTermToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        term = self.context
        token = term.token
        title = term.title if ITitledTokenizedTerm.providedBy(term) else token
        return {
            'token': token,
            'title': title
        }
