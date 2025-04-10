import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import os
import time
import dotenv
from freelancer_scraper import FreelancerScraper

class FreelancerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Freelancer Scraper")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Set theme colors
        self.bg_color = "#f0f0f0"
        self.accent_color = "#3498db"
        self.accent_hover = "#2980b9"
        self.text_color = "#2c3e50"
        self.success_color = "#2ecc71"
        self.error_color = "#e74c3c"
        self.error_hover = "#c0392b"
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TLabelframe", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.text_color, font=("Arial", 10, "bold"))
        
        # Flag to track if search is running
        self.searching = False
        self.stop_requested = False
        
        # Load environment variables
        dotenv.load_dotenv()
        
        # Check if credentials exist
        self.email = os.getenv("FREELANCER_EMAIL")
        self.password = os.getenv("FREELANCER_PASSWORD")
        
        if not self.email or not self.password:
            messagebox.showerror("Hata", "Lütfen .env dosyasında FREELANCER_EMAIL ve FREELANCER_PASSWORD değişkenlerini tanımlayın.")
            root.destroy()
            return
        
        self.create_widgets()
        
        # Configure window background
        self.root.configure(bg=self.bg_color)
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title frame with gradient-like effect
        title_frame = tk.Frame(main_frame, bg=self.accent_color, height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title
        title_label = tk.Label(title_frame, text="Freelancer.com İlan Arama", 
                              font=("Arial", 18, "bold"), 
                              fg="white", bg=self.accent_color)
        title_label.pack(pady=15)
        
        # Search frame
        search_frame = ttk.LabelFrame(main_frame, text="Arama Ayarları", padding="15")
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search keyword
        keyword_frame = ttk.Frame(search_frame)
        keyword_frame.pack(fill=tk.X, pady=5)
        
        keyword_label = ttk.Label(keyword_frame, text="Arama Kelimesi:", width=15)
        keyword_label.pack(side=tk.LEFT, padx=5)
        
        self.keyword_entry = ttk.Entry(keyword_frame, font=("Arial", 10))
        self.keyword_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        default_keyword = os.getenv("SEARCH_KEYWORD", "")
        if default_keyword:
            self.keyword_entry.insert(0, default_keyword)
        
        # Max pages
        pages_frame = ttk.Frame(search_frame)
        pages_frame.pack(fill=tk.X, pady=10)
        
        pages_label = ttk.Label(pages_frame, text="Maksimum Sayfa:", width=15)
        pages_label.pack(side=tk.LEFT, padx=5)
        
        self.pages_var = tk.StringVar(value=os.getenv("MAX_PAGES", "3"))
        self.pages_spinbox = ttk.Spinbox(pages_frame, from_=1, to=20, textvariable=self.pages_var, width=5, font=("Arial", 10))
        self.pages_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Button frame
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Custom Button design
        button_font = ("Arial", 10, "bold")
        
        # Search button (using tk.Button instead of ttk.Button for better color control)
        self.search_button = tk.Button(
            button_frame, 
            text="Ara", 
            font=button_font,
            bg=self.accent_color,
            fg="white",
            activebackground=self.accent_hover,
            activeforeground="white",
            width=15,
            relief=tk.RAISED,
            borderwidth=1,
            command=self.start_search
        )
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_button = tk.Button(
            button_frame, 
            text="Durdur", 
            font=button_font,
            bg=self.error_color, 
            fg="white",
            activebackground=self.error_hover,
            activeforeground="white",
            width=15,
            relief=tk.RAISED,
            borderwidth=1,
            state=tk.DISABLED,
            command=self.stop_search
        )
        self.stop_button.pack(side=tk.LEFT)
        
        # Results and log frame
        results_frame = ttk.LabelFrame(main_frame, text="Sonuçlar ve Log", padding="15")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log text area with custom styling
        self.log_text = scrolledtext.ScrolledText(
            results_frame, 
            wrap=tk.WORD, 
            height=15,
            font=("Consolas", 10),
            bg="#fafafa",
            fg=self.text_color
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text.config(state=tk.DISABLED)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='indeterminate', variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X)
        
        # Status bar
        self.status_var = tk.StringVar(value="Hazır")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, background="#f5f5f5")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def log_message(self, message, message_type="info"):
        """Add message to log text area with formatting based on message type"""
        self.log_text.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = time.strftime("[%H:%M:%S] ", time.localtime())
        self.log_text.insert(tk.END, timestamp, "timestamp")
        
        # Set tag based on message type
        if message_type == "error":
            tag = "error"
        elif message_type == "success":
            tag = "success"
        elif message_type == "warning":
            tag = "warning"
        else:
            tag = "info"
        
        # Insert message with appropriate tag
        self.log_text.insert(tk.END, message + "\n", tag)
        
        # Configure tags
        self.log_text.tag_configure("timestamp", foreground="#7f8c8d")
        self.log_text.tag_configure("info", foreground=self.text_color)
        self.log_text.tag_configure("success", foreground=self.success_color)
        self.log_text.tag_configure("error", foreground=self.error_color)
        self.log_text.tag_configure("warning", foreground="#f39c12")
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def start_search(self):
        """Start the search process in a separate thread"""
        # Get search parameters
        keyword = self.keyword_entry.get().strip()
        
        if not keyword:
            messagebox.showerror("Hata", "Lütfen bir arama kelimesi girin.")
            return
        
        try:
            max_pages = int(self.pages_var.get())
            if max_pages <= 0:
                messagebox.showerror("Hata", "Maksimum sayfa sayısı en az 1 olmalıdır.")
                return
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayfa sayısı girin.")
            return
        
        # Update UI state
        self.searching = True
        self.stop_requested = False
        self.search_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start progress bar
        self.progress_bar.start(10)
        
        # Clear log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # Start search thread
        search_thread = threading.Thread(target=self.run_search, args=(keyword, max_pages))
        search_thread.daemon = True
        search_thread.start()
    
    def stop_search(self):
        """Request to stop the search process"""
        if not self.searching:
            return
            
        self.log_message("Tarama durdurma isteği gönderildi. Lütfen bekleyin...", "warning")
        self.update_status("Durduruluyor...")
        self.stop_requested = True
        self.stop_button.config(state=tk.DISABLED)
    
    def run_search(self, keyword, max_pages):
        """Run the search in a separate thread"""
        try:
            self.update_status("Arama başlatılıyor...")
            self.log_message(f"Arama başlatılıyor: '{keyword}', {max_pages} sayfa", "info")
            self.log_message(f"Kullanıcı adı: {self.email}", "info")
            self.log_message("Tarayıcı açılıyor...", "info")
            
            # Create a custom print function to redirect output to our log
            original_print = print
            def custom_print(*args, **kwargs):
                if self.stop_requested:
                    raise Exception("Kullanıcı tarafından durduruldu")
                    
                message = " ".join(map(str, args))
                self.log_message(message)
                original_print(*args, **kwargs)
            
            # Replace the global print function temporarily
            import builtins
            builtins.print = custom_print
            
            # Run the scraper
            start_time = time.time()
            scraper = None
            
            try:
                # Create and run scraper
                scraper = FreelancerScraper(self.email, self.password, keyword, max_pages)
                
                # Store scraper instance in case we need to access browser
                self.current_scraper = scraper
                
                # Run the scraper
                scraper.run()
                
                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                minutes, seconds = divmod(elapsed_time, 60)
                
                # Output file path
                output_file = os.path.join("freelancer_data", f"freelancer_{keyword.replace(' ', '_')}.csv")
                
                # Check if data was collected
                if os.path.exists(output_file):
                    self.log_message(f"Tarama tamamlandı! Veriler {output_file} dosyasına kaydedildi.", "success")
                    self.log_message(f"Toplam işlem süresi: {int(minutes)} dakika {int(seconds)} saniye", "success")
                    self.update_status(f"Tamamlandı - {output_file} dosyasına kaydedildi")
                    messagebox.showinfo("Başarılı", f"Tarama tamamlandı!\nVeriler {output_file} dosyasına kaydedildi.")
                else:
                    self.log_message("Tarama tamamlandı fakat veri kaydedilmedi.", "warning")
                    self.log_message("Hata mesajlarını kontrol edin ve ekran görüntülerine bakın.", "warning")
                    self.update_status("Tamamlandı - Veri kaydedilemedi")
                    messagebox.warning("Uyarı", "Tarama tamamlandı fakat veri kaydedilmedi.")
            except Exception as e:
                error_msg = str(e)
                if "Kullanıcı tarafından durduruldu" in error_msg:
                    self.log_message("Tarama kullanıcı tarafından durduruldu.", "warning")
                    self.update_status("Durduruldu")
                    messagebox.showinfo("Durduruldu", "Tarama işlemi kullanıcı tarafından durduruldu.")
                else:
                    self.log_message(f"Bir hata oluştu: {e}", "error")
                    self.log_message("Hata ekran görüntüleri freelancer_data klasörüne kaydedilmiştir.", "error")
                    self.update_status("Hata oluştu")
                    messagebox.error("Hata", f"Bir hata oluştu: {e}")
                
                # Try to close browser if exists
                if scraper and hasattr(scraper, 'driver') and scraper.driver:
                    try:
                        scraper.driver.quit()
                    except:
                        pass
            finally:
                # Restore original print function
                builtins.print = original_print
                self.current_scraper = None
        finally:
            # Stop progress bar
            self.progress_bar.stop()
            
            # Reset UI state
            self.searching = False
            self.stop_requested = False
            
            # Re-enable search button and disable stop button
            self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))

def main():
    # Create root window
    root = tk.Tk()
    app = FreelancerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 