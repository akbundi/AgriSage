# agrisage/rag_store.py
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

def simple_normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s\-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str) -> List[str]:
    return simple_normalize(text).split()

def cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a.keys()) & set(b.keys())
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

@dataclass
class Doc:
    id: str
    text: str
    meta: Dict[str, Any] = field(default_factory=dict)

class MiniVectorStore:
    def __init__(self):
        self.docs: Dict[str, Doc] = {}
        self.df: Counter = Counter()
        self.tok_cache: Dict[str, List[str]] = {}
        self.doc_tf: Dict[str, Counter] = {}
        self.N: int = 0

    def _tokens(self, text: str) -> List[str]:
        if text in self.tok_cache:
            return self.tok_cache[text]
        toks = tokenize(text)
        self.tok_cache[text] = toks
        return toks

    def upsert(self, doc: Doc):
        if doc.id in self.docs:
            old_tokens = self._tokens(self.docs[doc.id].text)
            for t in set(old_tokens):
                self.df[t] -= 1
                if self.df[t] <= 0:
                    del self.df[t]
        self.docs[doc.id] = doc
        tokens = self._tokens(doc.text)
        tf = Counter(tokens)
        self.doc_tf[doc.id] = tf
        for t in set(tokens):
            self.df[t] += 1
        self.N = len(self.docs)

    def _tfidf(self, tf: Counter) -> Dict[str, float]:
        vec = {}
        for term, freq in tf.items():
            df = self.df.get(term, 0) + 1e-9
            idf = math.log((self.N + 1) / df)
            vec[term] = (1.0 + math.log(1 + freq)) * idf
        return vec

    def embed_query(self, q: str) -> Dict[str, float]:
        return self._tfidf(Counter(self._tokens(q)))

    def embed_doc(self, doc_id: str) -> Dict[str, float]:
        return self._tfidf(self.doc_tf.get(doc_id, Counter()))

    def top_k(self, query: str, k: int = 5) -> List[Tuple[Doc, float]]:
        qv = self.embed_query(query)
        scored = []
        for did, doc in self.docs.items():
            dv = self.embed_doc(did)
            scored.append((doc, cosine(qv, dv)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]
