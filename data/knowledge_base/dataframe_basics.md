# pandas Temelleri: Series ve DataFrame

## Temel Yapılar
pandas'ta iki temel veri yapısı vardır: **Series** (tek boyutlu, etiketli bir dizi) ve
**DataFrame** (iki boyutlu, satır ve sütunları etiketli bir tablo). Bir DataFrame, aslında
aynı indekse sahip birden fazla Series'in bir araya gelmesi olarak düşünülebilir.

## İndeksleme: loc vs iloc
- **`.loc[]`**: Etiket tabanlı indeksleme yapar. `df.loc[2, "isim"]` gibi, indeks etiketine ve
  sütun adına göre erişim sağlar. Dilim (slice) alırken son değeri DAHİL eder — bu, Python'un
  standart dilimleme davranışından farklıdır ve sık yapılan bir hatadır.
- **`.iloc[]`**: Tam sayı pozisyonuna göre indeksleme yapar (Python listeleri gibi). `df.iloc[0:2]`
  ilk iki satırı alır, standart Python dilimleme kuralına uyar (son değer dahil değildir).
- Karışık kullanım (örn. `df[df["a"] > 5]["b"] = 1`) genellikle bir "SettingWithCopyWarning"
  uyarısına yol açar; bunun yerine `.loc[df["a"] > 5, "b"] = 1` kullanılmalıdır.

## Veri Tipleri (dtypes)
Her sütunun bir `dtype`'ı vardır (int64, float64, object, category, datetime64, bool vb.).
`object` tipi genellikle string veya karışık tip verileri temsil eder ve bellekte en pahalı
tiptir. Sütunun sınırlı sayıda tekrarlayan değeri varsa (örn. şehir isimleri, durum kodları),
bunu `category` tipine dönüştürmek bellek kullanımını önemli ölçüde azaltır.

## Kopya mı, Görünüm mü? (Copy vs View)
pandas'ta bir DataFrame'in bir alt kümesini seçmek bazen bir "view" (orijinal veriye referans),
bazen bir "copy" (bağımsız kopya) döndürür ve bu davranış her zaman açık değildir. Bu belirsizlik,
"SettingWithCopyWarning" uyarısının temel nedenidir. Güvenli olmak için, bir alt küme üzerinde
değişiklik yapmadan önce `.copy()` ile açıkça bir kopya oluşturmak iyi bir pratiktir.

## Yaygın Hata: Zincirleme Atama (Chained Assignment)
`df[df["kolon"] > 0]["diger_kolon"] = 5` gibi zincirleme bir atama, beklenmedik şekilde
orijinal DataFrame'i DEĞİŞTİRMEYEBİLİR çünkü ara adım bir kopya döndürmüş olabilir. Doğru
yaklaşım her zaman `.loc[]` ile tek adımda atama yapmaktır.
