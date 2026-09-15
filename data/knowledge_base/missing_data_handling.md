# pandas'ta Eksik Veri Yönetimi

## Eksik Veri Temsili
pandas'ta eksik veri, sayısal sütunlarda `NaN` (Not a Number), tarih sütunlarında `NaT`
(Not a Time), nesne sütunlarında ise `None` veya `NaN` olarak temsil edilir. `pd.isna()` ve
`pd.notna()` fonksiyonları, tüm bu temsil biçimlerini tutarlı şekilde tespit eder.

## Tespit ve Özet
- `df.isna().sum()`: Her sütundaki eksik değer sayısını verir.
- `df.isna().mean() * 100`: Her sütundaki eksik değer YÜZDESİNİ verir — hangi sütunların
  ciddi veri kalitesi sorunu olduğunu hızlıca görmek için kullanışlıdır.

## Doldurma Stratejileri
- `df.fillna(0)`: Sabit bir değerle doldurma.
- `df.fillna(df.mean())`: Sütun ortalamasıyla doldurma (sayısal sütunlar için yaygın).
- `df.fillna(method="ffill")` (veya `df.ffill()`): Bir önceki geçerli değeri ileri taşır —
  zaman serisi verisinde (örn. sensör okumaları) sık kullanılır.
- `df.interpolate()`: Sayısal sütunlarda, komşu değerler arasında doğrusal (veya başka bir
  yöntemle) ara değer hesaplayarak doldurma yapar.

## Silme Stratejileri
- `df.dropna()`: Herhangi bir sütununda eksik değer olan TÜM satırları siler (varsayılan,
  `how="any"`). Çok agresif olabilir.
- `df.dropna(thresh=3)`: Sadece belirli bir eşiğin (örn. en az 3 dolu değer) altındaki
  satırları siler — kısmi eksik veriye toleranslı bir yaklaşımdır.
- `df.dropna(subset=["kritik_kolon"])`: Sadece belirtilen sütun(lar)da eksik olan satırları siler.

## Hangi Stratejiyi Seçmeli?
Doldurma mı silme mi kullanılacağı, eksikliğin NEDENİNE bağlıdır: Eğer veri "rastgele eksikse"
(MCAR — missing completely at random), silme genellikle güvenlidir. Eğer eksiklik başka bir
değişkenle ilişkiliyse (örn. belirli bir sensör türü daha sık veri kaybediyor), silme sonuçları
sistematik olarak çarpıtabilir ve doldurma (özellikle bağlama duyarlı yöntemlerle) tercih
edilmelidir.
