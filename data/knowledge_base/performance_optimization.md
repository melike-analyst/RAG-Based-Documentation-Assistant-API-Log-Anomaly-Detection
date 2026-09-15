# pandas Performans Optimizasyonu

## Vektörizasyon vs apply()
pandas ve NumPy'ın temel gücü VEKTÖRİZE işlemlerden gelir — yani bir döngü yazmak yerine,
işlemi tüm sütuna/diziye aynı anda uygulamak. `df["a"] + df["b"]` gibi bir işlem, C seviyesinde
optimize edilmiş kod çalıştırır. Buna karşılık `df.apply(lambda row: row["a"] + row["b"], axis=1)`,
her satır için Python seviyesinde bir fonksiyon çağrısı yapar ve genellikle 10-100 kat daha
yavaştır. Kural: eğer işlem NumPy/pandas'ın yerleşik fonksiyonlarıyla ifade edilebiliyorsa,
`apply()` kullanmaktan kaçınılmalıdır.

## Bellek Kullanımını Azaltma
- **category dtype**: Sınırlı sayıda tekrarlayan string değeri olan sütunlar (örn. şehir, durum
  kodu) `category` tipine dönüştürülürse, pandas her benzersiz değeri bir kez saklar ve
  satırlarda sadece bir tam sayı referansı tutar — bellek kullanımını çoğu zaman %50-90 azaltır.
- **Daha küçük sayısal tipler**: Varsayılan `int64`/`float64` yerine, değer aralığı uygunsa
  `int32`, `int16` veya `float32` kullanmak belleği yarıya indirebilir.
- **Gereksiz sütunları erken düşürme**: `usecols` parametresiyle `read_csv()` sırasında sadece
  gerekli sütunları okumak, tüm dosyayı yükleyip sonra sütun silmekten çok daha verimlidir.

## Büyük Dosyaları Parça Parça (Chunking) Okuma
Bellekte tek seferde tutulamayacak kadar büyük CSV dosyaları için, `pd.read_csv(path,
chunksize=100000)` bir iterator döndürür; her parça ayrı ayrı işlenip sonuçlar biriktirilebilir.
Bu, "tüm veriyi belleğe yükle" yaklaşımının pratik olmadığı durumlarda standart bir çözümdür.

## eval() ve query() ile Hızlandırma
Çok büyük DataFrame'lerde, `df.eval("c = a + b")` ve `df.query("a > 5 and b < 10")` gibi
string-tabanlı ifadeler, ara geçici (intermediate) NumPy dizilerinin oluşturulmasını önleyerek
(numexpr kütüphanesi varsa) standart sözdizimine göre daha hızlı ve daha az bellek kullanan
sonuçlar verebilir.

## Profilleme Önce, Optimizasyon Sonra
Performans optimizasyonuna başlamadan önce, gerçek darboğazın nerede olduğunu `%timeit` (Jupyter'de)
veya `cProfile` gibi araçlarla ölçmek önemlidir — sezgisel olarak "yavaş" görünen bir işlem,
toplam çalışma süresinin küçük bir kısmını oluşturuyor olabilir.
