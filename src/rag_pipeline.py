"""
rag_pipeline.py
-----------------
pandas dokümantasyon asistanı için Retrieval-Augmented Generation pipeline'ı:
  1) Kullanıcı sorgusunu TF-IDF indeksiyle en alakalı chunk'lara eşler (retrieval),
  2) Bu chunk'ları kaynak referanslarıyla birlikte bir prompt'a yerleştirir,
  3) Seçilen LLM sağlayıcısına (Anthropic veya OpenAI) gönderip cevap üretir,
  4) Cevabı, hangi kaynak dosyalardan geldiği bilgisiyle birlikte döner.

LLM sağlayıcısı ortam değişkeni ile seçilir:
  RAG_LLM_PROVIDER=anthropic  -> ANTHROPIC_API_KEY gerekir
  RAG_LLM_PROVIDER=openai     -> OPENAI_API_KEY gerekir
  (Hiçbiri ayarlı değilse, sadece retrieval sonuçlarını döner; kod hatasız çalışmaya devam eder.)
"""

import os
import pickle
from dataclasses import dataclass
from typing import List, Optional

from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = "data/knowledge_base_index.pkl"
TOP_K = 4

SYSTEM_PROMPT = """Sen pandas kütüphanesi hakkında bir teknik dokümantasyon asistanısın. Sana
verilen KAYNAK METİNLER dışında bilgi uydurma. Eğer verilen kaynaklarda sorunun cevabı yoksa,
açıkça 'Bu bilgi sağlanan kaynaklarda mevcut değil' de ve tahmin yürütme. Cevaplarını kısa,
teknik olarak doğru ve mümkünse kod örneğiyle destekleyerek ver."""


@dataclass
class RetrievedChunk:
    source_file: str
    chunk_id: str
    text: str
    score: float


@dataclass
class RagAnswer:
    query: str
    answer: str
    retrieved_chunks: List[RetrievedChunk]
    llm_used: bool


class Retriever:
    def __init__(self, index_path: str = INDEX_PATH):
        with open(index_path, "rb") as f:
            data = pickle.load(f)
        self.vectorizer = data["vectorizer"]
        self.matrix = data["matrix"]
        self.chunks = data["chunks"]

    def retrieve(self, query: str, top_k: int = TOP_K) -> List[RetrievedChunk]:
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = scores.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] <= 0:
                continue
            c = self.chunks[idx]
            results.append(RetrievedChunk(
                source_file=c["source_file"], chunk_id=c["chunk_id"],
                text=c["text"], score=float(scores[idx]),
            ))
        return results


def _build_prompt(query: str, chunks: List[RetrievedChunk]) -> str:
    context_blocks = "\n\n".join(f"[Kaynak: {c.source_file}]\n{c.text}" for c in chunks)
    return f"""KAYNAK METİNLER:
{context_blocks}

SORU: {query}

Yukarıdaki kaynak metinlere dayanarak soruyu cevapla. Cevabının sonunda hangi kaynak dosya(lar)dan
yararlandığını belirt."""


def _call_anthropic(prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=600, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if hasattr(block, "text"))


def _call_openai(prompt: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
        max_tokens=600,
    )
    return response.choices[0].message.content


def generate_answer(query: str, retriever: Optional[Retriever] = None) -> RagAnswer:
    retriever = retriever or Retriever()
    chunks = retriever.retrieve(query)

    if not chunks:
        return RagAnswer(query=query, answer="Bu konuda bilgi tabanında ilgili bir kaynak bulunamadı.",
                          retrieved_chunks=[], llm_used=False)

    prompt = _build_prompt(query, chunks)
    provider = os.getenv("RAG_LLM_PROVIDER", "").lower()

    try:
        if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
            answer_text = _call_anthropic(prompt)
            llm_used = True
        elif provider == "openai" and os.getenv("OPENAI_API_KEY"):
            answer_text = _call_openai(prompt)
            llm_used = True
        else:
            answer_text = (
                "[LLM yapılandırılmadı — RAG_LLM_PROVIDER ve ilgili API anahtarını ayarlayın.]\n\n"
                "En alakalı kaynak parçaları:\n" +
                "\n---\n".join(f"({c.source_file}) {c.text}" for c in chunks)
            )
            llm_used = False
    except Exception as e:
        answer_text = f"[LLM çağrısı başarısız oldu: {e}]"
        llm_used = False

    return RagAnswer(query=query, answer=answer_text, retrieved_chunks=chunks, llm_used=llm_used)


if __name__ == "__main__":
    test_queries = [
        "loc ile iloc arasındaki fark nedir?",
        "Büyük bir CSV dosyasını bellek dolmadan nasıl okurum?",
        "merge() ile concat() arasındaki fark nedir?",
        "pandas'ta GPU hızlandırması nasıl aktif edilir?",  # kaynakta olmayan, tuzak soru
    ]
    for q in test_queries:
        result = generate_answer(q)
        print(f"\nSORU: {q}")
        print(f"CEVAP: {result.answer[:400]}")
        print(f"Kullanılan kaynaklar: {[c.source_file for c in result.retrieved_chunks]}")
        print(f"LLM kullanıldı mı: {result.llm_used}")
