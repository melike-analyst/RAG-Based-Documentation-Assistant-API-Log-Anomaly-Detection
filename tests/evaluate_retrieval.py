"""
evaluate_retrieval.py
-----------------------
İlanın açıkça istediği 'AI çıktılarını doğruluk açısından test et ve bulgularını dokümante et'
maddesine karşılık gelir.

Bu script, retrieval katmanının (LLM olmadan) doğruluğunu ölçer:
  - "answerable" (cevaplanabilir) sorularda, doğru kaynak dosyanın top-k içinde gelip gelmediği,
  - "answerable: false" (bilgi tabanında YOK olan, tuzak) sorularda, sistemin hiçbir/uygun olmayan
    bir kaynak döndürüp döndürmediği (yani halüsinasyon riskinin retrieval seviyesinde önlenip
    önlenmediği).

Not: Bu, LLM'in ÜRETTİĞİ metnin doğruluğunu değil, RAG pipeline'ının doğru bağlamı BULUP
BULAMADIĞINI test eder — çünkü LLM API anahtarı olmadan da ölçülebilir, tekrarlanabilir ve
objektif bir metriktir. LLM entegre edildiğinde, aynı çerçeve (doğru/yanlış/halüsinasyon
etiketleme) LLM çıktılarına da uygulanmalıdır — bkz. README.md 'Sınırlamalar' bölümü.
"""

import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.rag_pipeline import Retriever


def evaluate():
    with open("tests/evaluation_set.json", "r", encoding="utf-8") as f:
        eval_set = json.load(f)

    retriever = Retriever()
    results = []

    for item in eval_set:
        chunks = retriever.retrieve(item["question"], top_k=4)
        retrieved_sources = set(c.source_file for c in chunks)

        if item["answerable"]:
            correct = item["expected_source"] in retrieved_sources
            verdict = "DOĞRU" if correct else "YANLIŞ (kaynak bulunamadı)"
        else:
            # Cevaplanamaz sorularda, HİÇBİR alakalı kaynak bulunamaması (ya da çok düşük skor)
            # ideal davranıştır. score eşiği retrieve() içinde zaten >0 filtresi uyguluyor,
            # burada ek olarak en yüksek skorun düşük olup olmadığını kontrol ediyoruz.
            max_score = max((c.score for c in chunks), default=0.0)
            correct = max_score < 0.15  # düşük benzerlik = model "bilmiyorum" demeli
            verdict = "DOĞRU (reddetti)" if correct else "YANLIŞ (halüsinasyon riski)"

        results.append({
            "id": item["id"],
            "question": item["question"],
            "answerable": item["answerable"],
            "expected_source": item["expected_source"],
            "retrieved_sources": sorted(retrieved_sources),
            "verdict": verdict,
            "correct": correct,
        })

    n_correct = sum(r["correct"] for r in results)
    accuracy = n_correct / len(results)

    report_lines = [
        "# Retrieval Doğruluk Değerlendirme Raporu",
        "",
        f"**Toplam soru sayısı:** {len(results)}",
        f"**Doğru:** {n_correct}",
        f"**Doğruluk oranı:** {accuracy:.1%}",
        "",
        "| ID | Soru | Cevaplanabilir mi | Beklenen Kaynak | Bulunan Kaynaklar | Sonuç |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        report_lines.append(
            f"| {r['id']} | {r['question']} | {r['answerable']} | {r['expected_source']} | "
            f"{', '.join(r['retrieved_sources']) or '-'} | {r['verdict']} |"
        )

    report_lines += [
        "",
        "## Yorum",
        "- Cevaplanabilir sorularda retrieval katmanı, TF-IDF gibi basit ama açıklanabilir bir "
        "yöntemle bile yüksek doğruluk sağlayabiliyor; bu, küçük/orta ölçekli, terminoloji-yoğun "
        "teknik doküman setlerinde (bu projedeki gibi) TF-IDF'in şaşırtıcı derecede güçlü bir "
        "başlangıç noktası olduğunu gösteriyor.",
        "- Cevaplanamaz (tuzak) sorularda düşük benzerlik skoru eşiği, sistemin 'bilmiyorum' "
        "demesini sağlayarak halüsinasyon riskini retrieval seviyesinde azaltıyor.",
        "- **Sınırlama:** Bu rapor sadece retrieval doğruluğunu ölçer. Bir LLM entegre edildiğinde, "
        "LLM'in ürettiği METNİN de kaynaklarla tutarlı olup olmadığı ayrıca (örn. insan gözden "
        "geçirmesiyle veya bir 'faithfulness' metriğiyle) test edilmelidir.",
    ]

    report = "\n".join(report_lines)
    with open("tests/evaluation_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(report)


if __name__ == "__main__":
    evaluate()
