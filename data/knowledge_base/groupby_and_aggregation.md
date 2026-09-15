# pandas'ta Gruplama ve Agregasyon

## groupby Mantığı
`df.groupby("kategori")` çağrısı, veriyi hemen işlemez; bunun yerine "split-apply-combine"
(böl-uygula-birleştir) desenini uygulayacak tembel (lazy) bir GroupBy nesnesi döndürür. Gerçek
hesaplama, üzerine `.sum()`, `.mean()`, `.agg()` gibi bir agregasyon fonksiyonu çağrıldığında
gerçekleşir.

## Tek ve Çoklu Agregasyon
- Tek sütun, tek fonksiyon: `df.groupby("kategori")["tutar"].sum()`
- Aynı sütuna birden fazla fonksiyon: `df.groupby("kategori")["tutar"].agg(["sum", "mean", "count"])`
- Farklı sütunlara farklı fonksiyonlar: `df.groupby("kategori").agg({"tutar": "sum", "adet": "mean"})`
- Adlandırılmış agregasyon (pandas ≥0.25): `df.groupby("kategori").agg(toplam=("tutar", "sum"))`
  bu, sonuç sütun isimlerini daha okunabilir hale getirir.

## pivot_table vs groupby
`pivot_table`, groupby'ın üzerine inşa edilmiş, sonucu iki boyutlu bir tabloya (satır/sütun
başlıkları ile) yeniden şekillendiren bir fonksiyondur. Genellikle raporlama ve özet tablolar
için groupby'dan daha okunabilir bir çıktı verir, ancak arka planda benzer bir mantık çalışır.

## transform() ile Grup İçi Hesaplama
`groupby(...).transform()`, agregasyon sonucunu ORİJİNAL DataFrame'in boyutuna geri yayarak
döndürür (agregasyon gibi satır sayısını azaltmaz). Bu, "her satırın, kendi grubunun ortalamasına
göre sapmasını hesapla" gibi işlemler için idealdir: `df["sapma"] = df["deger"] - df.groupby("grup")["deger"].transform("mean")`.

## Performans Notu
Büyük veri setlerinde, `groupby(...).apply(custom_function)` kullanımı, yerleşik (built-in)
agregasyon fonksiyonlarına (`sum`, `mean`, `agg` ile string isim verme) göre önemli ölçüde daha
yavaştır çünkü Python seviyesinde bir döngüye düşer. Mümkün olduğunda yerleşik fonksiyonlar veya
vektörize edilmiş NumPy işlemleri tercih edilmelidir.
