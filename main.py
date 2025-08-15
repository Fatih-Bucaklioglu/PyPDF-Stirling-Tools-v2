#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyPDF-Stirling Tools v2.0
Modern PDF işleme uygulaması
Fatih Bucaklıoğlu tarafından geliştirilmiştir.
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import time

# GUI kütüphaneleri
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import tkinter.font as tkFont
except ImportError:
    print("Tkinter modülü bulunamadı. Lütfen Python'ı GUI desteği ile kurun.")
    sys.exit(1)

# Proje modülleri
from ui.header import ModernHeader
from ui.sidebar import ModernSidebar
from ui.content import ModernContent
from utils import ConfigManager, CacheManager, LogManager, ThemeManager
from resources.pdf_utils import PDFProcessor
from ocr_module import OCRProcessor

# Sürüm bilgisi
__version__ = "2.0.0"
__author__ = "Fatih Bucaklıoğlu"
__description__ = "Modern PDF İşleme Uygulaması"

class PyPDFToolsV2:
    """
    PyPDF-Stirling Tools v2 Ana Uygulama Sınıfı
    """
    
    def __init__(self):
        """Ana uygulamayı başlat"""
        self.root = None
        self.config_manager = None
        self.cache_manager = None
        self.log_manager = None
        self.theme_manager = None
        self.pdf_processor = None
        self.ocr_processor = None
        
        # UI bileşenleri
        self.header = None
        self.sidebar = None
        self.content = None
        
        # Uygulama durumu
        self.current_files = []
        self.current_operation = None
        self.is_processing = False
        self.script_engine = None
        self.automation_engine = None
        
        # Çoklu işlem desteği
        self.worker_threads = []
        self.max_workers = os.cpu_count() or 4
        
    def initialize_application(self):
        """Uygulamayı başlat ve tüm bileşenleri hazırla"""
        try:
            # Loglama sistemini başlat
            self.setup_logging()
            self.log_manager.info("PyPDF Tools v2 başlatılıyor...")
            
            # Konfigürasyon yöneticisini başlat
            self.config_manager = ConfigManager()
            
            # Cache yöneticisini başlat
            self.cache_manager = CacheManager(
                enabled=self.config_manager.get('privacy.save_cache', False)
            )
            
            # Tema yöneticisini başlat
            self.theme_manager = ThemeManager()
            
            # Ana pencereyi oluştur
            self.create_main_window()
            
            # İşleme motorlarını başlat
            self.initialize_processors()
            
            # UI bileşenlerini oluştur
            self.create_ui_components()
            
            # Gelişmiş özellikler
            self.initialize_advanced_features()
            
            # Olay dinleyicilerini ayarla
            self.setup_event_handlers()
            
            # İlk çalıştırma kontrolü
            self.check_first_run()
            
            self.log_manager.info("Uygulama başarıyla başlatıldı")
            
        except Exception as e:
            self.handle_startup_error(e)
    
    def setup_logging(self):
        """Loglama sistemini ayarla"""
        self.log_manager = LogManager()
        
        # Log seviyesini ayarla
        log_level = logging.INFO
        if self.config_manager and self.config_manager.get('debug_mode', False):
            log_level = logging.DEBUG
        
        self.log_manager.set_level(log_level)
    
    def create_main_window(self):
        """Ana pencereyi oluştur"""
        self.root = tk.Tk()
        self.root.title(f"PyPDF-Stirling Tools v{__version__}")
        self.root.withdraw()  # İlk başta gizle
        
        # Pencere boyutları
        window_width = self.config_manager.get('appearance.window_size.width', 1400)
        window_height = self.config_manager.get('appearance.window_size.height', 900)
        
        # Ekran ortasında konumlandır
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 700)
        
        # Modern pencere stilleri
        self.root.configure(bg='#ffffff')
        
        # Pencere ikonu ayarla
        self.set_window_icon()
        
        # Pencere kapatma olayı
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def set_window_icon(self):
        """Pencere ikonunu ayarla"""
        try:
            icon_path = Path(__file__).parent / "icons" / "app_icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
            else:
                # Varsayılan ikon oluştur
                self.create_default_icon()
        except Exception as e:
            self.log_manager.warning(f"İkon ayarlanamadı: {e}")
    
    def create_default_icon(self):
        """Varsayılan uygulama ikonu oluştur"""
        try:
            # tkinter ile basit bir ikon oluştur
            from tkinter import PhotoImage
            import base64
            
            # Base64 kodlu basit PDF ikonu
            icon_data = """
            R0lGODlhEAAQAPQAAP///wAAAPDw8IqKiuDg4EZGRnp6egAAAFhYWCQkJKysrL6+vhQUFAQEBDY2
            NnJyciIiIlpaWvb29jIyMtjY2KCgoEpKSujo6Dg4ONzc3PLy8ra2tgAAAAAAAAAAAAAAAAAAACH5
            BAAAAAAALAAAAAAQABAAAAVVICSOZGlCQAqsJJoZH1MZlEDrAKHMIDFAOLbOKYXSjGYC2gAcC4jN6K
            o9lFoFKolECZwBmAoBOi+VygOywHfgFO1gCrCgFOUIg+Gzm/P+wHUQHgIAOw==
            """
            
            icon = PhotoImage(data=icon_data)
            self.root.iconphoto(True, icon)
        except Exception as e:
            self.log_manager.debug(f"Varsayılan ikon oluşturulamadı: {e}")
    
    def initialize_processors(self):
        """PDF ve OCR işlemcilerini başlat"""
        try:
            # PDF işlemcisi
            self.pdf_processor = PDFProcessor(
                cache_manager=self.cache_manager,
                log_manager=self.log_manager,
                max_workers=self.max_workers
            )
            
            # OCR işlemcisi
            ocr_languages = self.config_manager.get('ocr.installed_languages', ['eng', 'tur'])
            self.ocr_processor = OCRProcessor(
                languages=ocr_languages,
                cache_enabled=self.cache_manager.enabled,
                log_manager=self.log_manager
            )
            
            self.log_manager.info("İşleme motorları başarıyla başlatıldı")
            
        except Exception as e:
            self.log_manager.error(f"İşleme motorları başlatılamadı: {e}")
            messagebox.showerror("Hata", f"İşleme motorları başlatılamadı:\n{e}")
    
    def create_ui_components(self):
        """UI bileşenlerini oluştur"""
        try:
            # Header (Üst panel)
            self.header = ModernHeader(
                parent=self.root,
                config_manager=self.config_manager,
                theme_manager=self.theme_manager,
                app_instance=self
            )
            
            # Ana çerçeve
            main_frame = ttk.Frame(self.root)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
            
            # Sidebar (Sol menü)
            self.sidebar = ModernSidebar(
                parent=main_frame,
                config_manager=self.config_manager,
                theme_manager=self.theme_manager,
                app_instance=self
            )
            
            # Content (Ana içerik)
            self.content = ModernContent(
                parent=main_frame,
                config_manager=self.config_manager,
                theme_manager=self.theme_manager,
                pdf_processor=self.pdf_processor,
                ocr_processor=self.ocr_processor,
                app_instance=self
            )
            
            # Layout
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
            self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            
            # Tema uygula
            current_theme = self.config_manager.get('appearance.theme', 'light')
            self.theme_manager.apply_theme(current_theme, self.root)
            
            self.log_manager.info("UI bileşenleri başarıyla oluşturuldu")
            
        except Exception as e:
            self.log_manager.error(f"UI bileşenleri oluşturulamadı: {e}")
            messagebox.showerror("Hata", f"Arayüz oluşturulamadı:\n{e}")
    
    def initialize_advanced_features(self):
        """Gelişmiş özellikleri başlat"""
        try:
            # Script motoru
            from features.script_engine import ScriptEngine
            self.script_engine = ScriptEngine(
                app_instance=self,
                log_manager=self.log_manager
            )
            
            # Otomasyon motoru
            from features.automation_engine import AutomationEngine
            self.automation_engine = AutomationEngine(
                app_instance=self,
                config_manager=self.config_manager,
                log_manager=self.log_manager
            )
            
            # PDF okuyucu
            from features.pdf_viewer import PDFViewer
            self.pdf_viewer = PDFViewer(
                parent=self.root,
                theme_manager=self.theme_manager,
                config_manager=self.config_manager
            )
            
            # Sistem entegrasyonu
            self.setup_system_integration()
            
            self.log_manager.info("Gelişmiş özellikler başarıyla başlatıldı")
            
        except ImportError as e:
            self.log_manager.warning(f"Bazı gelişmiş özellikler kullanılamıyor: {e}")
        except Exception as e:
            self.log_manager.error(f"Gelişmiş özellikler başlatılamadı: {e}")
    
    def setup_system_integration(self):
        """Sistem entegrasyonu ayarla"""
        try:
            # Sistem tepsisi desteği
            if self.config_manager.get('system.system_tray', True):
                self.setup_system_tray()
            
            # Dosya ilişkilendirmesi
            if self.config_manager.get('system.file_association', False):
                self.setup_file_association()
            
            # Komut satırı desteği
            self.setup_cli_support()
            
        except Exception as e:
            self.log_manager.warning(f"Sistem entegrasyonu ayarlanamadı: {e}")
    
    def setup_system_tray(self):
        """Sistem tepsisi ayarla"""
        try:
            import pystray
            from PIL import Image
            
            # Tray ikonu oluştur
            icon_path = Path(__file__).parent / "icons" / "tray_icon.png"
            if not icon_path.exists():
                # Basit bir ikon oluştur
                image = Image.new('RGB', (64, 64), color='blue')
            else:
                image = Image.open(icon_path)
            
            # Tray menüsü
            menu = pystray.Menu(
                pystray.MenuItem("Göster", self.show_window),
                pystray.MenuItem("Gizle", self.hide_window),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Çıkış", self.quit_application)
            )
            
            # Tray ikonu oluştur
            self.tray_icon = pystray.Icon("PyPDF Tools v2", image, menu=menu)
            
            # Ayrı thread'de çalıştır
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
            
        except ImportError:
            self.log_manager.debug("pystray modülü bulunamadı, sistem tepsisi devre dışı")
        except Exception as e:
            self.log_manager.warning(f"Sistem tepsisi ayarlanamadı: {e}")
    
    def setup_event_handlers(self):
        """Olay dinleyicilerini ayarla"""
        try:
            # Dosya sürükle-bırak desteği
            self.setup_drag_and_drop()
            
            # Klavye kısayolları
            self.setup_keyboard_shortcuts()
            
            # Pencere olayları
            self.root.bind("<Configure>", self.on_window_configure)
            
        except Exception as e:
            self.log_manager.error(f"Olay dinleyicileri ayarlanamadı: {e}")
    
    def setup_drag_and_drop(self):
        """Sürükle-bırak desteğini ayarla"""
        try:
            import tkinterdnd2 as tkdnd
            
            # Root'u DnD uyumlu yap
            self.root = tkdnd.TkinterDnD.dnd_aware(self.root)
            
            # Drop olaylarını bağla
            self.content.bind_dnd_events()
            
        except ImportError:
            self.log_manager.debug("tkinterdnd2 modülü bulunamadı, sürükle-bırak devre dışı")
    
    def setup_keyboard_shortcuts(self):
        """Klavye kısayollarını ayarla"""
        shortcuts = {
            '<Control-o>': self.open_files,
            '<Control-s>': self.save_current_work,
            '<Control-q>': self.quit_application,
            '<F1>': self.show_help,
            '<F11>': self.toggle_fullscreen,
            '<Control-comma>': self.show_settings,
            '<Control-Shift-i>': self.show_developer_tools
        }
        
        for shortcut, handler in shortcuts.items():
            self.root.bind(shortcut, lambda e, h=handler: h())
    
    def check_first_run(self):
        """İlk çalıştırma kontrolü"""
        is_first_run = self.config_manager.get('app.first_run', True)
        
        if is_first_run:
            self.show_welcome_wizard()
            self.config_manager.set('app.first_run', False)
            self.config_manager.save()
    
    def show_welcome_wizard(self):
        """Karşılama sihirbazını göster"""
        try:
            from ui.welcome_wizard import WelcomeWizard
            wizard = WelcomeWizard(
                parent=self.root,
                config_manager=self.config_manager,
                theme_manager=self.theme_manager
            )
            wizard.show()
        except ImportError:
            self.log_manager.debug("Karşılama sihirbazı modülü bulunamadı")
    
    def run(self):
        """Uygulamayı çalıştır"""
        try:
            # Pencereyi göster
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            
            # Ana döngüyü başlat
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.log_manager.info("Uygulama kullanıcı tarafından durduruldu")
            self.quit_application()
        except Exception as e:
            self.log_manager.error(f"Uygulama çalıştırılırken hata: {e}")
            self.handle_runtime_error(e)
    
    def on_closing(self):
        """Pencere kapatma olayı"""
        try:
            # Ayarları kaydet
            self.save_window_state()
            
            # İşlemleri temizle
            self.cleanup_processes()
            
            # Cache temizle (gerekirse)
            if not self.config_manager.get('privacy.save_cache', False):
                self.cache_manager.clear_all()
            
            # Logları kaydet
            self.log_manager.info("Uygulama kapatılıyor")
            
            # Pencereyi kapat
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            self.log_manager.error(f"Kapanış sırasında hata: {e}")
        finally:
            sys.exit(0)
    
    def save_window_state(self):
        """Pencere durumunu kaydet"""
        try:
            geometry = self.root.geometry()
            width, height, x, y = map(int, geometry.replace('x', '+').split('+'))
            
            self.config_manager.set('appearance.window_size.width', width)
            self.config_manager.set('appearance.window_size.height', height)
            self.config_manager.set('appearance.window_position.x', x)
            self.config_manager.set('appearance.window_position.y', y)
            
            self.config_manager.save()
            
        except Exception as e:
            self.log_manager.error(f"Pencere durumu kaydedilemedi: {e}")
    
    def cleanup_processes(self):
        """İşlemleri temizle"""
        try:
            # Çalışan worker thread'leri durdur
            for thread in self.worker_threads:
                if thread.is_alive():
                    thread.join(timeout=5)
            
            # Otomasyon motorunu durdur
            if self.automation_engine:
                self.automation_engine.stop()
            
            # Cache temizle
            if self.cache_manager and not self.cache_manager.enabled:
                self.cache_manager.clear_all()
            
        except Exception as e:
            self.log_manager.error(f"İşlemler temizlenirken hata: {e}")
    
    def handle_startup_error(self, error):
        """Başlangıç hatalarını işle"""
        error_msg = f"Uygulama başlatılamadı:\n{str(error)}"
        
        # Konsola yazdır
        print(error_msg)
        
        # GUI varsa mesaj göster
        try:
            if self.root:
                messagebox.showerror("Başlangıç Hatası", error_msg)
        except:
            pass
        
        sys.exit(1)
    
    def handle_runtime_error(self, error):
        """Çalışma zamanı hatalarını işle"""
        error_msg = f"Beklenmeyen hata:\n{str(error)}"
        
        if self.log_manager:
            self.log_manager.error(error_msg)
        
        try:
            messagebox.showerror("Hata", error_msg)
        except:
            print(error_msg)
    
    # UI Event Handlers
    def on_window_configure(self, event):
        """Pencere boyut değişikliği olayı"""
        if event.widget == self.root:
            # Responsive tasarım ayarları
            self.update_responsive_layout()
    
    def update_responsive_layout(self):
        """Responsive layout güncelle"""
        try:
            width = self.root.winfo_width()
            
            # Küçük ekranlar için sidebar'ı gizle/göster
            if width < 1200:
                self.sidebar.configure_for_small_screen()
            else:
                self.sidebar.configure_for_large_screen()
                
        except Exception as e:
            self.log_manager.debug(f"Responsive layout güncellenemedi: {e}")
    
    # Public Methods
    def open_files(self):
        """Dosya açma diyalogunu göster"""
        if self.content:
            self.content.open_files_dialog()
    
    def save_current_work(self):
        """Mevcut çalışmayı kaydet"""
        if self.content:
            self.content.save_current_work()
    
    def show_settings(self):
        """Ayarlar penceresini göster"""
        try:
            from ui.settings_dialog import SettingsDialog
            dialog = SettingsDialog(
                parent=self.root,
                config_manager=self.config_manager,
                theme_manager=self.theme_manager
            )
            dialog.show()
        except ImportError:
            messagebox.showinfo("Bilgi", "Ayarlar penceresi henüz mevcut değil")
    
    def show_help(self):
        """Yardım penceresini göster"""
        try:
            from ui.help_dialog import HelpDialog
            dialog = HelpDialog(parent=self.root)
            dialog.show()
        except ImportError:
            messagebox.showinfo("Yardım", f"PyPDF-Stirling Tools v{__version__}\n\n{__description__}")
    
    def show_developer_tools(self):
        """Geliştirici araçlarını göster"""
        try:
            from ui.developer_tools import DeveloperTools
            tools = DeveloperTools(
                parent=self.root,
                app_instance=self,
                log_manager=self.log_manager
            )
            tools.show()
        except ImportError:
            messagebox.showinfo("Bilgi", "Geliştirici araçları henüz mevcut değil")
    
    def toggle_fullscreen(self):
        """Tam ekran modunu aç/kapat"""
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
    
    def show_window(self):
        """Pencereyi göster"""
        self.root.deiconify()
        self.root.lift()
    
    def hide_window(self):
        """Pencereyi gizle"""
        self.root.withdraw()
    
    def quit_application(self):
        """Uygulamadan çık"""
        self.on_closing()

def main():
    """Ana fonksiyon"""
    try:
        # Komut satırı argümanlarını işle
        if len(sys.argv) > 1:
            from cli.cli_handler import CLIHandler
            cli_handler = CLIHandler()
            result = cli_handler.handle_args(sys.argv[1:])
            sys.exit(result)
        
        # GUI uygulamasını başlat
        app = PyPDFToolsV2()
        app.initialize_application()
        app.run()
        
    except Exception as e:
        print(f"Kritik hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()