# Retrieval Doğruluk Değerlendirme Raporu

**Toplam soru sayısı:** 15
**Doğru:** 13
**Doğruluk oranı:** 86.7%

| ID | Soru | Cevaplanabilir mi | Beklenen Kaynak | Bulunan Kaynaklar | Sonuç |
|---|---|---|---|---|---|
| q1 | loc ile iloc arasındaki fark nedir? | True | dataframe_basics.md | dataframe_basics.md, merging_and_joining.md | DOĞRU |
| q2 | SettingWithCopyWarning neden ortaya çıkar? | True | dataframe_basics.md | dataframe_basics.md | DOĞRU |
| q3 | category dtype ne zaman kullanılmalı? | True | dataframe_basics.md | dataframe_basics.md, missing_data_handling.md, performance_optimization.md | DOĞRU |
| q4 | groupby().transform() ne işe yarar? | True | groupby_and_aggregation.md | groupby_and_aggregation.md | DOĞRU |
| q5 | pivot_table ile groupby arasındaki fark nedir? | True | groupby_and_aggregation.md | groupby_and_aggregation.md | DOĞRU |
| q6 | merge() işleminde validate parametresi ne işe yarar? | True | merging_and_joining.md | merging_and_joining.md | DOĞRU |
| q7 | concat() ile merge() arasındaki fark nedir? | True | merging_and_joining.md | merging_and_joining.md | DOĞRU |
| q8 | fillna ile dropna arasında nasıl karar verilir? | True | missing_data_handling.md | merging_and_joining.md, missing_data_handling.md | DOĞRU |
| q9 | NaN ve NaT arasındaki fark nedir? | True | missing_data_handling.md | groupby_and_aggregation.md, merging_and_joining.md, missing_data_handling.md | DOĞRU |
| q10 | apply() neden bazen çok yavaş olur? | True | performance_optimization.md | dataframe_basics.md, groupby_and_aggregation.md, performance_optimization.md | DOĞRU |
| q11 | Büyük bir CSV dosyasını bellek dolmadan nasıl okurum? | True | performance_optimization.md | merging_and_joining.md, performance_optimization.md | DOĞRU |
| q12 | pandas'ta GPU hızlandırması nasıl aktif edilir? | False | None | groupby_and_aggregation.md, merging_and_joining.md, missing_data_handling.md | YANLIŞ (halüsinasyon riski) |
| q13 | pandas'ın en son sürümünde eklenen yeni özellikler nelerdir? | False | None | dataframe_basics.md, missing_data_handling.md, performance_optimization.md | DOĞRU (reddetti) |
| q14 | pandas ile derin öğrenme modeli nasıl eğitilir? | False | None | dataframe_basics.md, groupby_and_aggregation.md, missing_data_handling.md, performance_optimization.md | YANLIŞ (halüsinasyon riski) |
| q15 | Polars pandas'tan nasıl farklıdır? | False | None | dataframe_basics.md, groupby_and_aggregation.md, missing_data_handling.md, performance_optimization.md | DOĞRU (reddetti) |

## Yorum
- Cevaplanabilir sorularda retrieval katmanı, TF-IDF gibi basit ama açıklanabilir bir yöntemle bile yüksek doğruluk sağlayabiliyor; bu, küçük/orta ölçekli, terminoloji-yoğun teknik doküman setlerinde (bu projedeki gibi) TF-IDF'in şaşırtıcı derecede güçlü bir başlangıç noktası olduğunu gösteriyor.
- Cevaplanamaz (tuzak) sorularda düşük benzerlik skoru eşiği, sistemin 'bilmiyorum' demesini sağlayarak halüsinasyon riskini retrieval seviyesinde azaltıyor.
- **Sınırlama:** Bu rapor sadece retrieval doğruluğunu ölçer. Bir LLM entegre edildiğinde, LLM'in ürettiği METNİN de kaynaklarla tutarlı olup olmadığı ayrıca (örn. insan gözden geçirmesiyle veya bir 'faithfulness' metriğiyle) test edilmelidir.