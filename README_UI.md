# Freelancer Scraper Arayüzü

Bu uygulama, Freelancer.com üzerindeki ilanları aramak ve sonuçları CSV dosyasına kaydetmek için geliştirilmiş bir arayüz sunar.

## Kurulum

1. Gerekli Python paketlerini yükleyin:
   ```
   pip install selenium python-dotenv pandas tkinter
   ```

2. Selenium için Chrome WebDriver'ı indirip yüklediğinizden emin olun.

3. `.env` dosyasını düzenleyerek Freelancer.com hesap bilgilerinizi girin:
   ```
   FREELANCER_EMAIL=kullanıcı_adınız
   FREELANCER_PASSWORD=şifreniz
   ```

## Kullanım

1. Arayüzü başlatmak için:
   ```
   python freelancer_ui.py
   ```

2. Açılan arayüzde:
   - "Arama Kelimesi" alanına aramak istediğiniz terimi girin (örn. "web developer")
   - "Maksimum Sayfa" kısmında kaç sayfa taranacağını belirleyin
   - "Ara" butonuna tıklayın

3. Tarama işlemi başlayacak ve işlem adımları log bölümünde gösterilecektir.

4. İşlem tamamlandığında sonuçlar CSV dosyası olarak `freelancer_data` klasörüne kaydedilecektir.

## Özellikler

- Kullanıcı dostu grafiksel arayüz
- Arama terimini ve maksimum sayfa sayısını belirleyebilme
- İşlem durumunu gerçek zamanlı olarak görebilme
- Hata durumunda bilgilendirme ve ekran görüntüleri alma
- Arkaplanda asenkron çalışma (uygulama donmaz)

## Notlar

- Kullanıcı adı ve şifre bilgileri `.env` dosyasından alınır, arayüzden girilmesine gerek yoktur.
- Tarayıcı penceresini kapatmayın veya minimize etmeyin, bu işlemin başarısız olmasına neden olabilir.
- Tarama işlemi sırasında internet bağlantınızın iyi olduğundan emin olun.
- Bazı durumlarda Freelancer.com'un bot koruması devreye girebilir, bu durumda manuel olarak CAPTCHA'yı çözmeniz gerekebilir. 