"""
build_knowledge_base.py
-------------------------
data/knowledge_base/ altındaki markdown dokümanlarını okur, anlamlı parçalara (chunk) böler ve
TF-IDF tabanlı bir retrieval indeksi oluşturup diske kaydeder.

NEDEN TF-IDF (embedding modeli değil)?
Bu sandbox ortamında model ağırlığı indirmeyi gerektiren büyük embedding modellerine (örn.
sentence-transformers, HuggingFace Hub) ağ erişimi kısıtlı olduğundan, tamamen offline çalışan,
klasik ve açıklanabilir bir yöntem olan TF-IDF + kosinüs benzerliği tercih edilmiştir. Üretim
ortamında bu modül, aynı arayüzü koruyarak (bkz. Retriever sınıfı) kolayca bir embedding tabanlı
vektör veritabanına (Chroma, FAISS + OpenAI/Voyage embeddings vb.) yükseltilebilir — bu, README'de
"Nasıl Geliştirilir" bölümünde açıkça not edilmiştir.
"""

import os
import re
import json
import pickle
from dataclasses import dataclass, asdict
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer

KB_DIR = "data/knowledge_base"
INDEX_PATH = "data/knowledge_base_index.pkl"
CHUNK_SIZE_WORDS = 120
CHUNK_OVERLAP_WORDS = 20


@dataclass
class Chunk:
    doc_id: str
    chunk_id: str
    source_file: str
    text: str


def _chunk_text(text: str, source_file: str) -> List[Chunk]:
    """Basit kelime-tabanlı, overlap'li chunking. Markdown başlıklarını (##) chunk sınırlarına
    yakın tutmaya çalışır ki bağlam kaybı minimize edilsin."""
    # Başlıkları koruyarak paragraflara böl
    paragraphs = re.split(r"\n(?=#{1,3} )", text)
    chunks = []
    chunk_counter = 0

    for para in paragraphs:
        words = para.split()
        if len(words) <= CHUNK_SIZE_WORDS:
            if words:
                chunk_counter += 1
                chunks.append(Chunk(
                    doc_id=source_file,
                    chunk_id=f"{source_file}::chunk{chunk_counter}",
                    source_file=source_file,
                    text=para.strip(),
                ))
            continue

        start = 0
        while start < len(words):
            end = start + CHUNK_SIZE_WORDS
            chunk_words = words[start:end]
            chunk_counter += 1
            chunks.append(Chunk(
                doc_id=source_file,
                chunk_id=f"{source_file}::chunk{chunk_counter}",
                source_file=source_file,
                text=" ".join(chunk_words).strip(),
            ))
            start = end - CHUNK_OVERLAP_WORDS

    return chunks


def load_and_chunk_documents() -> List[Chunk]:
    all_chunks = []
    for filename in sorted(os.listdir(KB_DIR)):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(KB_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        all_chunks.extend(_chunk_text(text, filename))
    return all_chunks


def build_index():
    chunks = load_and_chunk_documents()
    texts = [c.text for c in chunks]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_df=0.9,
        min_df=1,
    )
    matrix = vectorizer.fit_transform(texts)

    with open(INDEX_PATH, "wb") as f:
        pickle.dump({
            "vectorizer": vectorizer,
            "matrix": matrix,
            "chunks": [asdict(c) for c in chunks],
        }, f)

    print(f"{len(chunks)} chunk indekslendi -> {INDEX_PATH}")
    print(f"Kaynak dosyalar: {sorted(set(c.source_file for c in chunks))}")


if __name__ == "__main__":
    build_index()
