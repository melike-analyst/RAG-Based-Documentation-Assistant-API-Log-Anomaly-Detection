# pandas'ta Birleştirme İşlemleri: merge, join, concat

## merge()
`pd.merge(df1, df2, on="anahtar", how="inner")`, SQL'deki JOIN mantığına en yakın fonksiyondur.
`how` parametresi ile birleştirme tipi belirlenir:
- `inner`: Sadece her iki tabloda da eşleşen anahtarlar
- `left` / `right`: Bir tarafın tüm satırları korunur, eşleşmeyenler NaN ile doldurulur
- `outer`: Her iki taraftaki tüm anahtarlar korunur

## join()
`df1.join(df2)`, `merge()`'in indeks üzerinden birleştirmeye özelleşmiş, daha kısa bir
kısayoludur. Sütun adı yerine indeksleri eşleştirir. Anahtar sütun üzerinden birleştirme
gerekiyorsa `merge()` daha esnektir ve genellikle tercih edilir.

## concat()
`pd.concat([df1, df2])`, birleştirme (join mantığı) değil, EKLEME (satır veya sütun bazında
üst üste/yan yana koyma) yapar. `axis=0` (varsayılan) satırları alt alta ekler, `axis=1`
sütunları yan yana ekler. Farklı indekslere sahip DataFrame'leri `axis=1` ile birleştirirken,
indeksler hizalanır ve eşleşmeyen yerler NaN ile doldurulur.

## Yaygın Hata: Çoktan-Çoğa Eşleşmede Satır Patlaması
`merge()` işleminde her iki tabloda da anahtar sütununda tekrarlayan değerler varsa (çoktan-çoğa
ilişki), sonuç DataFrame'in satır sayısı beklenenden çok daha fazla olabilir (kartezyen çarpım
etkisi). Bu durumu önceden tespit etmek için `pd.merge(..., validate="one_to_one")` gibi
`validate` parametresi kullanılabilir; beklenmeyen bir ilişki tipi varsa hata fırlatır.

## Performans İpucu
Büyük tablo birleştirmelerinde, birleştirme anahtarının bir indeks olarak ayarlanması
(`set_index()`) ve `join()` kullanılması, `merge()`'e göre bazı durumlarda daha hızlı
olabilir çünkü pandas indeks üzerinden arama yapmak için optimize edilmiştir.
