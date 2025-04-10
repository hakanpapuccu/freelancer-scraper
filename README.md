# Freelancer.com İlan Scraper

Bu Python scripti, Selenium kullanarak Freelancer.com'daki ilanları otomatik olarak çekip CSV dosyasına kaydeder.

## Özellikler

- Freelancer.com'a otomatik giriş yapma
- Belirtilen anahtar kelime ile arama yapma
- İlan başlıklarını, açıklamalarını ve fiyat bilgilerini çekme
- Verileri CSV dosyasına kaydetme
- Sayfalama desteği ile birden fazla sayfadan veri çekme
- Çeşitli hata durumlarını ele alma ve ekran görüntüleri kaydetme

## Gereksinimler

- Python 3.6+
- Chrome tarayıcısı
- ChromeDriver (Chrome versiyonunuza uygun)
- Aşağıdaki Python paketleri:
  - selenium
  - pandas
  - python-dotenv

## Kurulum

1. Gerekli paketleri yükleyin:
```
pip install selenium pandas python-dotenv
```

2. ChromeDriver'ı [buradan](https://chromedriver.chromium.org/downloads) indirip PATH'e ekleyin veya script ile aynı dizine koyun.

3. `.env` dosyasını düzenleyin (Aşağıdaki ayarları kendi bilgilerinizle değiştirin):
```
FREELANCER_EMAIL=your_email@example.com
FREELANCER_PASSWORD=your_password
SEARCH_KEYWORD=web developer
MAX_PAGES=3
```

## Kullanım

1. `.env` dosyasını düzenledikten sonra, aşağıdaki komutu çalıştırın:
```
python run_scraper.py
```

2. Script otomatik olarak:
   - Freelancer.com'a giriş yapacak
   - Belirttiğiniz anahtar kelime ile arama yapacak
   - İlanları toplayacak
   - Verileri `freelancer_data` klasöründe bir CSV dosyasına kaydedecek

## Güvenlik Notları

- `.env` dosyasını asla paylaşmayın veya Git reposuna dahil etmeyin
- `.gitignore` dosyanıza `.env` eklemeyi unutmayın
- Hassas bilgileri korumak için her zaman `.env` dosyasını kullanın

## Sorun Giderme

- Giriş yapma sorunu: `.env` dosyasındaki kimlik bilgilerini kontrol edin
- Tarayıcı kapanma sorunu: Bekleme sürelerini artırın
- Elementin bulunamama sorunu: Hata ekran görüntülerini kontrol edin
- XPath sorunları: Site yapısı değişmiş olabilir, XPath'leri güncelleyin 