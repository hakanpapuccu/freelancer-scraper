import getpass
import os
import time
import dotenv
from freelancer_scraper import FreelancerScraper

def main():
    print("\n===== Freelancer.com İlan Scraper =====\n")
    print("Bu scraper Freelancer.com'dan ilan bilgilerini çekmek için kullanılır.")
    print("Önce giriş yapacak, ardından arama yapıp sonuçları kaydedecektir.\n")
    
    # Load environment variables from .env file
    dotenv.load_dotenv()
    
    # Get credentials from environment variables
    email = os.getenv("FREELANCER_EMAIL")
    password = os.getenv("FREELANCER_PASSWORD")
    search_term = os.getenv("SEARCH_KEYWORD")
    
    # Check if environment variables are set
    missing_vars = []
    if not email:
        missing_vars.append("FREELANCER_EMAIL")
    if not password:
        missing_vars.append("FREELANCER_PASSWORD")
    if not search_term:
        missing_vars.append("SEARCH_KEYWORD")
    
    # If any required variables are missing, exit and inform the user
    if missing_vars:
        print("Hata: Aşağıdaki değişkenler .env dosyasında tanımlanmamış:")
        for var in missing_vars:
            print(f"- {var}")
        print("\n.env dosyasını kontrol edin ve eksik değişkenleri ekleyin.")
        return
    
    # Get maximum number of pages to scrape from environment or ask user
    max_pages = os.getenv("MAX_PAGES")
    if max_pages:
        try:
            max_pages = int(max_pages)
            if max_pages <= 0:
                print("Uyarı: MAX_PAGES 0 veya negatif olamaz. Varsayılan değer (3) kullanılacak.")
                max_pages = 3
        except ValueError:
            print("Uyarı: MAX_PAGES geçerli bir sayı değil. Varsayılan değer (3) kullanılacak.")
            max_pages = 3
    else:
        # If MAX_PAGES is not in .env file, ask user
        while True:
            try:
                max_pages = int(input("Kaç sayfa taranacak (varsayılan: 3): ") or "3")
                if max_pages > 0:
                    break
                else:
                    print("Lütfen pozitif bir sayı girin.")
            except ValueError:
                print("Lütfen geçerli bir sayı girin.")
    
    # Confirm and run
    print("\nScraper aşağıdaki bilgilerle başlatılacak:")
    print(f"Email/Kullanıcı Adı: {email}")
    print(f"Arama kelimesi: {search_term}")
    print(f"Maksimum sayfa sayısı: {max_pages}")
    confirm = input("\nDevam etmek istiyor musunuz? (e/h): ")
    
    if confirm.lower() in ['e', 'y', 'evet', 'yes']:
        # Create output directory if it doesn't exist
        output_dir = "freelancer_data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, f"freelancer_{search_term.replace(' ', '_')}.csv")
        
        # Create and run the scraper
        print("\nTarayıcı açılıyor ve işlem başlatılıyor...\n")
        print("Not: Bu işlem biraz zaman alabilir, lütfen bekleyin.")
        print("İşlem devam ederken tarayıcıyı kapatmayın veya minimize etmeyin.")
        print("\nÖnemli: Scraper ilanları çekerken bir hata alırsa, ekran görüntüleri alarak")
        print("freelancer_data klasörüne kaydedecektir. Bu görüntüler sorunu çözmenize yardımcı olabilir.")
        
        try:
            start_time = time.time()
            
            # Print start time
            print(f"\nBaşlangıç zamanı: {time.strftime('%H:%M:%S', time.localtime())}")
            
            # Create and run scraper
            scraper = FreelancerScraper(email, password, search_term, max_pages)
            scraper.run()
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            minutes, seconds = divmod(elapsed_time, 60)
            
            # Check if data was collected
            if os.path.exists(output_file):
                print(f"\nTarama tamamlandı! Veriler {output_file} dosyasına kaydedildi.")
                print(f"Toplam işlem süresi: {int(minutes)} dakika {int(seconds)} saniye")
                print(f"Sonuçları görüntülemek için csv dosyasını açabilirsiniz.")
            else:
                print("\nTarama tamamlandı fakat veri kaydedilmedi.")
                print("Hata mesajlarını kontrol edin ve ekran görüntülerine bakın.")
                
        except KeyboardInterrupt:
            print("\nİşlem kullanıcı tarafından durduruldu.")
        except Exception as e:
            print(f"\nBir hata oluştu: {e}")
            print("Hata ekran görüntüleri freelancer_data klasörüne kaydedilmiştir.")
        finally:
            print("\nProgram sonlandı.")
    else:
        print("\nİşlem iptal edildi.")

if __name__ == "__main__":
    main() 