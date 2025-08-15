import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# Sınıf tanımının başladığını varsayıyoruz. 
# Örneğin: class ModernContent(ttk.Frame):
#            def __init__(self, parent, ...):
#                ...
#                self.create_content_area()

    def create_content_area(self):
        """Content area'yı oluştur"""
        self.configure(style='Content.TFrame')
        
        # Ana container
        main_container = ttk.Frame(self, style='ContentContainer.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Üst bölüm - Drop zone ve file list
        self.create_upper_section(main_container)
        
        # Orta bölüm - Options panel
        self.create_middle_section(main_container)
        
        # Alt bölüm - Progress ve results
        self.create_lower_section(main_container)
        
        # Varsayılan görünümü ayarla
        self.show_welcome_view()
    
    # --- BURADAN İTİBAREN TÜM METOTLAR BİR SEVİYE SAĞA KAYDIRILDI ---

    def create_upper_section(self, parent):
        """Üst bölüm oluştur"""
        upper_frame = ttk.Frame(parent, style='UpperSection.TFrame')
        upper_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Drop zone
        self.create_drop_zone(upper_frame)
        
        # File list (başlangıçta gizli)
        self.create_file_list(upper_frame)
    
    def create_drop_zone(self, parent):
        """Dosya sürükle-bırak alanı oluştur"""
        self.drop_zone = ttk.Frame(parent, style='DropZone.TFrame')
        self.drop_zone.pack(fill=tk.BOTH, expand=True)
        
        # Drop zone içeriği
        drop_content = ttk.Frame(self.drop_zone, style='DropZoneContent.TFrame')
        drop_content.place(relx=0.5, rely=0.5, anchor='center')
        
        # Drop ikonu
        self.drop_icon = tk.Canvas(
            drop_content,
            width=64,
            height=64,
            highlightthickness=0,
            relief='flat'
        )
        self.drop_icon.pack(pady=(0, 16))
        
        self.create_drop_icon()
        
        # Ana mesaj
        self.drop_title = ttk.Label(
            drop_content,
            text="PDF dosyalarınızı buraya sürükleyin",
            style='DropTitle.TLabel'
        )
        self.drop_title.pack(pady=(0, 8))
        
        # Alt mesaj
        self.drop_subtitle = ttk.Label(
            drop_content,
            text="veya dosya seçmek için tıklayın",
            style='DropSubtitle.TLabel'
        )
        self.drop_subtitle.pack(pady=(0, 20))
        
        # Dosya seçme butonu
        select_btn = ttk.Button(
            drop_content,
            text="📁 Dosya Seç",
            style='SelectFile.TButton',
            command=self.open_files_dialog
        )
        select_btn.pack(pady=(0, 10))
        
        # Desteklenen formatlar
        formats_label = ttk.Label(
            drop_content,
            text="Desteklenen: PDF, DOC, DOCX, JPG, PNG, TIFF",
            style='FormatsLabel.TLabel'
        )
        formats_label.pack()
        
        # Drop zone tıklama olayı
        self.drop_zone.bind('<Button-1>', lambda e: self.open_files_dialog())
        self.add_drop_zone_bindings()
    
    def create_drop_icon(self):
        """Drop ikonu oluştur"""
        self.drop_icon.delete("all")
        
        # Animasyonlu dosya ikonu
        # Dış çerçeve
        self.drop_icon.create_rectangle(
            16, 20, 48, 56,
            outline='#3b82f6',
            width=2,
            fill='',
            tags='file_outline'
        )
        
        # Dosya köşesi
        self.drop_icon.create_polygon(
            38, 20, 48, 30, 38, 30,
            outline='#3b82f6',
            fill='#dbeafe',
            width=2,
            tags='file_corner'
        )
        
        # İç çizgiler
        for i, y in enumerate([35, 40, 45]):
            self.drop_icon.create_line(
                22, y, 42, y,
                fill='#3b82f6',
                width=1,
                tags=f'file_line_{i}'
            )
        
        # Animasyon başlat
        self.animate_drop_icon()
    
    def animate_drop_icon(self):
        """Drop ikonu animasyonu"""
        def pulse():
            # Pulse efekti
            for scale in [1.0, 1.1, 1.0]:
                self.drop_icon.after(500, lambda s=scale: self.scale_drop_icon(s))
        
        # 3 saniyede bir tekrarla
        self.drop_icon.after(3000, pulse)
        pulse()
    
    def scale_drop_icon(self, scale):
        """Drop ikonu ölçeklendir"""
        try:
            self.drop_icon.scale("all", 32, 32, scale, scale)
        except tk.TclError:
            pass
    
    def add_drop_zone_bindings(self):
        """Drop zone olayları ekle"""
        # Drag enter
        def on_drag_enter(event):
            self.drop_zone.configure(style='DropZoneHover.TFrame')
            self.animate_drop_zone_enter()
        
        # Drag leave
        def on_drag_leave(event):
            self.drop_zone.configure(style='DropZone.TFrame')
            self.animate_drop_zone_leave()
        
        # Drop
        def on_drop(event):
            files = self.parse_drop_data(event.data)
            self.handle_dropped_files(files)
        
        # Mouse enter/leave
        self.drop_zone.bind('<Enter>', on_drag_enter)
        self.drop_zone.bind('<Leave>', on_drag_leave)
        
        # Drag and drop bindings (tkinterdnd2 gerekli)
        try:
            self.drop_zone.drop_target_register('DND_Files')
            self.drop_zone.dnd_bind('<<DropEnter>>', on_drag_enter)
            self.drop_zone.dnd_bind('<<DropLeave>>', on_drag_leave)
            self.drop_zone.dnd_bind('<<Drop>>', on_drop)
        except:
            pass  # DnD desteklenmiyorsa sessizce geç
    
    def create_file_list(self, parent):
        """Dosya listesi oluştur"""
        self.file_list_frame = ttk.Frame(parent, style='FileList.TFrame')
        # Başlangıçta gizli
        
        # Başlık
        list_header = ttk.Frame(self.file_list_frame, style='FileListHeader.TFrame')
        list_header.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            list_header,
            text="Seçilen Dosyalar",
            style='FileListTitle.TLabel'
        )
        title_label.pack(side=tk.LEFT)
        
        # Temizle butonu
        clear_btn = ttk.Button(
            list_header,
            text="🗑️ Temizle",
            style='ClearFiles.TButton',
            command=self.clear_files
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # Dosya ekleme butonu
        add_btn = ttk.Button(
            list_header,
            text="➕ Dosya Ekle",
            style='AddFiles.TButton',
            command=self.open_files_dialog
        )
        add_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Scrollable dosya listesi
        self.create_scrollable_file_list()
    
    def create_scrollable_file_list(self):
        """Kaydırılabilir dosya listesi"""
        # Frame ve scrollbar
        list_container = ttk.Frame(self.file_list_frame, style='FileListContainer.TFrame')
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas ve scrollbar
        self.files_canvas = tk.Canvas(
            list_container,
            highlightthickness=0,
            relief='flat',
            height=200
        )
        
        files_scrollbar = ttk.Scrollbar(
            list_container,
            orient='vertical',
            command=self.files_canvas.yview
        )
        
        self.files_scrollable_frame = ttk.Frame(self.files_canvas)
        
        # Layout
        self.files_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas ayarları
        self.files_canvas.configure(yscrollcommand=files_scrollbar.set)
        
        # Scrollable frame'i canvas'a ekle
        canvas_frame = self.files_canvas.create_window(
            (0, 0),
            window=self.files_scrollable_frame,
            anchor='nw'
        )
        
        # Scroll region güncelleme
        def configure_scroll_region(event):
            self.files_canvas.configure(scrollregion=self.files_canvas.bbox('all'))
        
        def configure_canvas_width(event):
            canvas_width = event.width
            self.files_canvas.itemconfig(canvas_frame, width=canvas_width)
        
        self.files_scrollable_frame.bind('<Configure>', configure_scroll_region)
        self.files_canvas.bind('<Configure>', configure_canvas_width)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            self.files_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.files_canvas.bind("<MouseWheel>", on_mousewheel)
    
    def create_middle_section(self, parent):
        """Orta bölüm - Options panel"""
        self.options_panel = ttk.Frame(parent, style='OptionsPanel.TFrame')
        # Başlangıçta gizli
        
        # Panel başlığı
        options_header = ttk.Frame(self.options_panel, style='OptionsPanelHeader.TFrame')
        options_header.pack(fill=tk.X, pady=(0, 15))
        
        self.options_title = ttk.Label(
            options_header,
            text="İşlem Ayarları",
            style='OptionsPanelTitle.TLabel'
        )
        self.options_title.pack(side=tk.LEFT)
        
        # İşlem seçici
        operation_frame = ttk.Frame(options_header, style='OperationFrame.TFrame')
        operation_frame.pack(side=tk.RIGHT)
        
        ttk.Label(
            operation_frame,
            text="İşlem:",
            style='OperationLabel.TLabel'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.operation_var = tk.StringVar()
        self.operation_combo = ttk.Combobox(
            operation_frame,
            textvariable=self.operation_var,
            state='readonly',
            style='Operation.TCombobox'
        )
        self.operation_combo.pack(side=tk.LEFT)
        self.operation_combo.bind('<<ComboboxSelected>>', self.on_operation_change)
        
        # Dinamik options container
        self.dynamic_options = ttk.Frame(self.options_panel, style='DynamicOptions.TFrame')
        self.dynamic_options.pack(fill=tk.X, pady=(0, 15))
        
        # Action buttons
        self.create_action_buttons()
    
    def create_action_buttons(self):
        """Aksiyon butonları oluştur"""
        actions_frame = ttk.Frame(self.options_panel, style='ActionsFrame.TFrame')
        actions_frame.pack(fill=tk.X)
        
        # Sol taraf - Output directory
        output_frame = ttk.Frame(actions_frame, style='OutputFrame.TFrame')
        output_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(
            output_frame,
            text="Çıktı Klasörü:",
            style='OutputLabel.TLabel'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_var = tk.StringVar()
        self.output_var.set(self.config_manager.get('pdf_processing.output_directory', '~/Desktop'))
        
        output_entry = ttk.Entry(
            output_frame,
            textvariable=self.output_var,
            style='OutputPath.TEntry'
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(
            output_frame,
            text="📁",
            style='BrowseOutput.TButton',
            width=3,
            command=self.browse_output_directory
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Sağ taraf - Process button
        self.process_btn = ttk.Button(
            actions_frame,
            text="🚀 İşlemi Başlat",
            style='ProcessButton.TButton',
            command=self.start_processing
        )
        self.process_btn.pack(side=tk.RIGHT, padx=(20, 0))
    
    def create_lower_section(self, parent):
        """Alt bölüm - Progress ve results"""
        lower_frame = ttk.Frame(parent, style='LowerSection.TFrame')
        lower_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Progress panel
        self.create_progress_panel(lower_frame)
        
        # Results panel
        self.create_results_panel(lower_frame)
    
    def create_progress_panel(self, parent):
        """Progress panel oluştur"""
        self.progress_panel = ttk.Frame(parent, style='ProgressPanel.TFrame')
        # Başlangıçta gizli
        
        # Progress header
        progress_header = ttk.Frame(self.progress_panel, style='ProgressHeader.TFrame')
        progress_header.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_title = ttk.Label(
            progress_header,
            text="İşlem Durumu",
            style='ProgressTitle.TLabel'
        )
        self.progress_title.pack(side=tk.LEFT)
        
        # Cancel button
        self.cancel_btn = ttk.Button(
            progress_header,
            text="❌ İptal",
            style='CancelButton.TButton',
            command=self.cancel_processing
        )
        self.cancel_btn.pack(side=tk.RIGHT)
        
        # Progress bars container
        progress_container = ttk.Frame(self.progress_panel, style='ProgressContainer.TFrame')
        progress_container.pack(fill=tk.X, pady=(0, 10))
        
        # Ana progress bar
        self.main_progress_var = tk.DoubleVar()
        self.main_progress = ttk.Progressbar(
            progress_container,
            variable=self.main_progress_var,
            maximum=100,
            style='Main.Horizontal.TProgressbar'
        )
        self.main_progress.pack(fill=tk.X, pady=(0, 5))
        
        # Progress text
        self.progress_text = ttk.Label(
            progress_container,
            text="Hazırlanıyor...",
            style='ProgressText.TLabel'
        )
        self.progress_text.pack(anchor='w')
        
        # Detaylı progress (dosya bazında)
        self.file_progress_frame = ttk.Frame(progress_container, style='FileProgress.TFrame')
        self.file_progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        # İstatistikler
        stats_frame = ttk.Frame(self.progress_panel, style='StatsFrame.TFrame')
        stats_frame.pack(fill=tk.X)
        
        self.stats_labels = {}
        stats_items = [
            ('processed', 'İşlenen: 0'),
            ('remaining', 'Kalan: 0'),
            ('errors', 'Hata: 0'),
            ('speed', 'Hız: 0 MB/s'),
            ('eta', 'Tahmini: --:--')
        ]
        
        for stat_id, initial_text in stats_items:
            label = ttk.Label(
                stats_frame,
                text=initial_text,
                style='StatsLabel.TLabel'
            )
            label.pack(side=tk.LEFT, padx=(0, 20))
            self.stats_labels[stat_id] = label
    
    def create_results_panel(self, parent):
        """Results panel oluştur"""
        self.results_panel = ttk.Frame(parent, style='ResultsPanel.TFrame')
        # Başlangıçta gizli
        
        # Results header
        results_header = ttk.Frame(self.results_panel, style='ResultsHeader.TFrame')
        results_header.pack(fill=tk.X, pady=(0, 10))
        
        results_title = ttk.Label(
            results_header,
            text="İşlem Sonuçları",
            style='ResultsTitle.TLabel'
        )
        results_title.pack(side=tk.LEFT)
        
        # Export results button
        export_btn = ttk.Button(
            results_header,
            text="💾 Rapor Kaydet",
            style='ExportResults.TButton',
            command=self.export_results
        )
        export_btn.pack(side=tk.RIGHT)
        
        # Open output folder button
        open_folder_btn = ttk.Button(
            results_header,
            text="📁 Klasörü Aç",
            style='OpenFolder.TButton',
            command=self.open_output_folder
        )
        open_folder_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Results treeview
        self.create_results_treeview()
    
    def create_results_treeview(self):
        """Results treeview oluştur"""
        tree_container = ttk.Frame(self.results_panel, style='TreeContainer.TFrame')
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Treeview ve scrollbar
        self.results_tree = ttk.Treeview(
            tree_container,
            style='Results.Treeview',
            columns=('file', 'operation', 'status', 'size', 'time'),
            show='headings',
            height=8
        )
        
        results_v_scrollbar = ttk.Scrollbar(
            tree_container,
            orient='vertical',
            command=self.results_tree.yview
        )
        
        results_h_scrollbar = ttk.Scrollbar(
            tree_container,
            orient='horizontal',
            command=self.results_tree.xview
        )
        
        # Layout
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        results_v_scrollbar.grid(row=0, column=1, sticky='ns')
        results_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # Scrollbar bağlantıları
        self.results_tree.configure(
            yscrollcommand=results_v_scrollbar.set,
            xscrollcommand=results_h_scrollbar.set
        )
        
        # Sütun ayarları
        columns = {
            'file': ('Dosya', 200),
            'operation': ('İşlem', 100),
            'status': ('Durum', 80),
            'size': ('Boyut', 80),
            'time': ('Süre', 80)
        }
        
        for col_id, (heading, width) in columns.items():
            self.results_tree.heading(col_id, text=heading)
            self.results_tree.column(col_id, width=width, minwidth=50)
        
        # Çift tıklama olayı
        self.results_tree.bind('<Double-1>', self.on_result_double_click)
    
    def setup_drag_and_drop(self):
        """Drag and drop sistemi ayarla"""
        try:
            import tkinterdnd2 as tkdnd
            
            # Drop zone'u DnD uyumlu yap
            self.drop_zone.drop_target_register('DND_Files')
            
            def handle_drop(event):
                files = self.parse_drop_data(event.data)
                self.handle_dropped_files(files)
            
            self.drop_zone.dnd_bind('<<Drop>>', handle_drop)
            
        except ImportError:
            # DnD desteği yok, sadece click-to-select
            pass
    
    def parse_drop_data(self, data):
        """Drop data'sını parse et"""
        if isinstance(data, str):
            # Windows ve Unix path'lerini handle et
            if data.startswith('{') and data.endswith('}'):
                # Windows path with spaces
                return [data[1:-1]]
            else:
                # Multiple files or Unix paths
                return data.split()
        return []
    
    def bind_dnd_events(self):
        """DnD eventlerini bind et"""
        # Header'dan çağrılacak
        pass
    
    # Event Handlers
    def animate_drop_zone_enter(self):
        """Drop zone'a girerken animasyon"""
        self.drop_title.configure(text="Dosyaları bırakın!")
        self.animate_drop_icon_hover()
    
    def animate_drop_zone_leave(self):
        """Drop zone'dan çıkarken animasyon"""
        self.drop_title.configure(text="PDF dosyalarınızı buraya sürükleyin")
    
    def animate_drop_icon_hover(self):
        """Drop icon hover animasyonu"""
        # İkonu büyüt
        self.scale_drop_icon(1.2)
        self.drop_zone.after(200, lambda: self.scale_drop_icon(1.0))
    
    def handle_dropped_files(self, files):
        """Bırakılan dosyaları işle"""
        valid_files = []
        
        for file_path in files:
            path = Path(file_path.strip('"\''))
            
            if path.exists() and path.is_file():
                # Desteklenen format kontrolü
                if self.is_supported_file(path):
                    valid_files.append(str(path))
        
        if valid_files:
            self.add_files(valid_files)
        else:
            messagebox.showwarning(
                "Uyarı",
                "Desteklenmeyen dosya formatı!\n\nDesteklenen formatlar:\n" +
                "PDF, DOC, DOCX, JPG, PNG, TIFF, BMP"
            )
    
    def is_supported_file(self, file_path):
        """Dosya formatı destekleniyor mu?"""
        supported_extensions = {
            '.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', 
            '.tiff', '.tif', '.bmp', '.gif', '.webp'
        }
        return file_path.suffix.lower() in supported_extensions
    
    def open_files_dialog(self):
        """Dosya seçme diyalogu"""
        filetypes = [
            ('PDF Dosyaları', '*.pdf'),
            ('Word Dosyaları', '*.doc *.docx'),
            ('Resim Dosyaları', '*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.gif'),
            ('Tüm Dosyalar', '*.*')
        ]
        
        initial_dir = self.config_manager.get('ui.last_open_directory', os.path.expanduser('~'))
        
        files = filedialog.askopenfilenames(
            title="PDF Dosyaları Seçin",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        if files:
            # Son açılan dizini kaydet
            last_dir = os.path.dirname(files[0])
            self.config_manager.set('ui.last_open_directory', last_dir)
            self.config_manager.save()
            
            self.add_files(files)
    
    def add_files(self, files):
        """Dosyaları listeye ekle"""
        new_files = []
        
        for file_path in files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                new_files.append(file_path)
        
        if new_files:
            self.update_file_list_display()
            self.show_file_list()
            self.animate_file_addition(len(new_files))
    
    def update_file_list_display(self):
        """Dosya listesi görüntüsünü güncelle"""
        # Mevcut öğeleri temizle
        for widget in self.files_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Her dosya için satır oluştur
        for i, file_path in enumerate(self.selected_files):
            self.create_file_item(self.files_scrollable_frame, file_path, i)
    
    def create_file_item(self, parent, file_path, index):
        """Dosya öğesi oluştur"""
        path = Path(file_path)
        
        # Ana frame
        item_frame = ttk.Frame(parent, style='FileItem.TFrame')
        item_frame.pack(fill=tk.X, pady=2)
        
        # Sol taraf - ikon ve bilgiler
        left_frame = ttk.Frame(item_frame, style='FileItemLeft.TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=8)
        
        # Dosya ikonu
        icon = self.get_file_icon(path.suffix.lower())
        icon_label = ttk.Label(
            left_frame,
            text=icon,
            style='FileIcon.TLabel'
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Dosya bilgileri
        info_frame = ttk.Frame(left_frame, style='FileInfo.TFrame')
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dosya adı
        name_label = ttk.Label(
            info_frame,
            text=path.name,
            style='FileName.TLabel'
        )
        name_label.pack(anchor='w')
        
        # Dosya yolu ve boyutu
        try:
            size = path.stat().st_size
            size_str = self.format_file_size(size)
        except:
            size_str = "Bilinmiyor"
        
        details_text = f"{path.parent} • {size_str}"
        details_label = ttk.Label(
            info_frame,
            text=details_text,
            style='FileDetails.TLabel'
        )
        details_label.pack(anchor='w')
        
        # Sağ taraf - aksiyonlar
        right_frame = ttk.Frame(item_frame, style='FileItemRight.TFrame')
        right_frame.pack(side=tk.RIGHT, padx=10)
        
        # Kaldır butonu
        remove_btn = ttk.Button(
            right_frame,
            text="🗑️",
            style='RemoveFile.TButton',
            width=3,
            command=lambda idx=index: self.remove_file(idx)
        )
        remove_btn.pack(side=tk.RIGHT)
        
        # Önizleme butonu (PDF için)
        if path.suffix.lower() == '.pdf':
            preview_btn = ttk.Button(
                right_frame,
                text="👁️",
                style='PreviewFile.TButton',
                width=3,
                command=lambda fp=file_path: self.preview_file(fp)
            )
            preview_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Hover efekti
        self.add_file_item_hover(item_frame)
    
    def get_file_icon(self, extension):
        """Dosya türüne göre ikon döndür"""
        icons = {
            '.pdf': '📄',
            '.doc': '📝', '.docx': '📝',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️',
            '.tiff': '🖼️', '.tif': '🖼️', '.bmp': '🖼️',
            '.gif': '🖼️', '.webp': '🖼️'
        }
        return icons.get(extension, '📎')
    
    def format_file_size(self, size):
        """Dosya boyutunu format et"""
        if size == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def add_file_item_hover(self, item_frame):
        """Dosya öğesi hover efekti"""
        original_style = item_frame.cget('style')
        
        def on_enter(event):
            item_frame.configure(style='FileItemHover.TFrame')
        
        def on_leave(event):
            item_frame.configure(style=original_style)
        
        item_frame.bind('<Enter>', on_enter)
        item_frame.bind('<Leave>', on_leave)
        
        # Alt widget'lara da bind et
        for child in item_frame.winfo_children():
            child.bind('<Enter>', on_enter)
            child.bind('<Leave>', on_leave)
    
    def remove_file(self, index):
        """Dosyayı listeden kaldır"""
        if 0 <= index < len(self.selected_files):
            removed_file = self.selected_files.pop(index)
            self.update_file_list_display()
            
            # Liste boşsa drop zone'u göster
            if not self.selected_files:
                self.show_welcome_view()
    
    def clear_files(self):
        """Tüm dosyaları temizle"""
        self.selected_files.clear()
        self.show_welcome_view()
    
    def preview_file(self, file_path):
        """Dosya önizlemesi göster"""
        try:
            if hasattr(self.app_instance, 'pdf_viewer'):
                self.app_instance.pdf_viewer.open_file(file_path)
            else:
                messagebox.showinfo("Bilgi", "PDF okuyucu henüz mevcut değil")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya açılamadı: {e}")
    
    def animate_file_addition(self, count):
        """Dosya ekleme animasyonu"""
        # Başarı mesajı göster
        self.show_notification(f"✅ {count} dosya eklendi", "success")
    
    def show_notification(self, message, type_="info"):
        """Bildirim göster"""
        # Basit notification sistemi
        notification = tk.Toplevel(self.winfo_toplevel())
        notification.overrideredirect(True)
        
        bg_color = 'green' if type_ == "success" else 'red' if type_ == "error" else '#3b82f6'
        
        notification.configure(bg=bg_color)
        
        label = ttk.Label(
            notification,
            text=message,
            background=bg_color,
            foreground='white',
            padding=10,
            font=("Fira Sans", 10, "bold")
        )
        label.pack(padx=1, pady=1)
        
        # Konumlandır
        parent = self.winfo_toplevel()
        x = parent.winfo_x() + parent.winfo_width() - label.winfo_reqwidth() - 30
        y = parent.winfo_y() + parent.winfo_height() - label.winfo_reqheight() - 30
        notification.geometry(f"+{x}+{y}")
        
        # 3 saniye sonra kapat
        notification.after(3000, notification.destroy)
    
    # View Management
    def show_welcome_view(self):
        """Karşılama görünümünü göster"""
        self.hide_all_panels()
        self.drop_zone.pack(fill=tk.BOTH, expand=True)
    
    def show_file_list(self):
        """Dosya listesini göster"""
        self.drop_zone.pack_forget()
        self.file_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Options panel'i göster
        if self.selected_files:
            self.show_options_panel()
    
    def show_options_panel(self):
        """Options panel'i göster"""
        self.options_panel.pack(fill=tk.X, pady=(0, 20))
        self.populate_operation_combo()
    
    def show_progress_panel(self):
        """Progress panel'i göster"""
        self.progress_panel.pack(fill=tk.X, pady=(0, 20))
    
    def show_results_panel(self):
        """Results panel'i göster"""
        self.results_panel.pack(fill=tk.X)
    
    def hide_all_panels(self):
        """Tüm panelleri gizle"""
        panels_to_check = ['file_list_frame', 'options_panel', 'progress_panel', 'results_panel']
        for panel_name in panels_to_check:
            if hasattr(self, panel_name):
                panel = getattr(self, panel_name)
                if panel:
                    panel.pack_forget()
    
    def populate_operation_combo(self):
        """Operation combo'yu doldur"""
        operations = [
            ('merge', '🔗 PDF Birleştir'),
            ('split', '✂️ PDF Böl'),
            ('compress', '🗜️ PDF Sıkıştır'),
            ('convert', '🔄 Format Dönüştür'),
            ('rotate', '↻ Sayfa Döndür'),
            ('extract_text', '📄 Metin Çıkar'),
            ('extract_images', '🖼️ Resim Çıkar'),
            ('watermark', '💧 Filigran Ekle'),
            ('encrypt', '🔐 Şifrele'),
            ('decrypt', '🔓 Şifre Kaldır'),
            ('ocr', '👁️ OCR Uygula'),
            ('optimize', '⚡ Optimize Et')
        ]
        
        self.operation_map = {name: id for id, name in operations}
        self.operation_combo['values'] = [op[1] for op in operations]
        
        # Varsayılan işlem
        if hasattr(self, 'current_operation') and self.current_operation:
            try:
                current_name = next(name for id, name in operations if id == self.current_operation)
                self.operation_combo.set(current_name)
            except StopIteration:
                self.operation_combo.current(0)
        else:
            self.operation_combo.current(0)
        
        self.on_operation_change()
    
    def on_operation_change(self, event=None):
        """İşlem değişikliği olayı"""
        selected_name = self.operation_combo.get()
        self.current_operation = self.operation_map.get(selected_name, 'merge')
        self.update_options_panel()
    
    def update_options_panel(self):
        """Options panel'ini güncelle"""
        # Mevcut dinamik seçenekleri temizle
        for widget in self.dynamic_options.winfo_children():
            widget.destroy()
        
        # Seçilen işleme göre seçenekleri oluştur
        self.create_operation_options()
    
    def create_operation_options(self):
        """İşlem seçeneklerini oluştur"""
        # Bu metodun çağrılacağı yer, her bir işlem için ayrı create_..._options metotlarını içermeli
        # Örnek:
        if self.current_operation == 'merge':
             pass # self.create_merge_options()
        elif self.current_operation == 'split':
             pass # self.create_split_options()
        # ...ve diğerleri
