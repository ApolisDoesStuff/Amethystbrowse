import pip
try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtWebEngineWidgets import *
    from PyQt5.QtPrintSupport import *
    from PyQt5.QtCore import QStandardPaths
    import os
    import sys
    import configparser
except ModuleNotFoundError:
    pip.main(['install', '--trusted-host', 'pypi.org', '--trusted-host', 'files.pythonhosted.org', 'pyqt5'])
    pip.main(['install', '--trusted-host', 'pypi.org', '--trusted-host', 'files.pythonhosted.org', 'pyqtwebengine'])
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtWebEngineWidgets import *
    from PyQt5.QtPrintSupport import *
    from PyQt5.QtCore import QStandardPaths
    import os
    import sys
    import configparser

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

CONFIG_FILE = 'config.ini'

# Load settings from config.ini file
def load_settings():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        # If the config file does not exist, use defaults
        return {
            'theme': 'Light',  # Default theme
            'search_engine': 'Google'  # Default search engine
        }
    config.read(CONFIG_FILE)
    return {
        'theme': config.get('Settings', 'theme', fallback='Light'),
        'search_engine': config.get('Settings', 'search_engine', fallback='Google')
    }

# Save settings to config.ini file
def save_settings(theme, search_engine):
    config = configparser.ConfigParser()
    if not config.has_section('Settings'):
        config.add_section('Settings')
    config.set('Settings', 'theme', theme)
    config.set('Settings', 'search_engine', search_engine)
    
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(600, 200, 400, 300)
        
        # Layout for the settings
        self.layout = QVBoxLayout()

        # Theme setting
        self.theme_label = QLabel("Choose Theme:")
        self.layout.addWidget(self.theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.layout.addWidget(self.theme_combo)

        # Search Engine setting
        self.search_label = QLabel("Choose Search Engine:")
        self.layout.addWidget(self.search_label)

        self.search_combo = QComboBox()
        self.search_combo.addItems(["Google", "DuckDuckGo", "Ecosia"])
        self.layout.addWidget(self.search_combo)

        # Apply button
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.apply_changes)
        self.layout.addWidget(self.apply_btn)

        self.setLayout(self.layout)

    def apply_changes(self):
        selected_theme = self.theme_combo.currentText()
        selected_search_engine = self.search_combo.currentText()
        
        # Apply theme changes
        if selected_theme == "Dark":
            self.parent().set_dark_theme()
        else:
            self.parent().set_light_theme()

        # Apply search engine changes
        self.parent().set_search_engine(selected_search_engine)

        # Save the settings to the config file
        save_settings(selected_theme, selected_search_engine)

        self.accept()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        profile = QWebEngineProfile()
        profile.setHttpUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537')

        # Load settings from config.ini
        settings = load_settings()
        self.theme = settings['theme']
        self.search_engine = settings['search_engine']

        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)
        self.add_new_tab()

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)
        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.go_back)
        navtb.addAction(back_btn)
        next_btn = QAction("Forward", self)
        next_btn.triggered.connect(self.go_forward)
        navtb.addAction(next_btn)
        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        navtb.addAction(reload_btn)
        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)
        stop_btn = QAction("Stop", self)
        stop_btn.triggered.connect(self.stop_loading)
        navtb.addAction(stop_btn)

        # Plus button for adding new tabs
        add_tab_btn = QAction("+", self)
        add_tab_btn.triggered.connect(lambda: self.add_new_tab())
        navtb.addAction(add_tab_btn)

        # Downloads button to show download manager
        download_btn = QAction("Downloads", self)
        download_btn.triggered.connect(self.show_downloads)
        navtb.addAction(download_btn)

        # Settings button to open the settings window
        settings_btn = QAction("Settings", self)
        settings_btn.triggered.connect(self.open_settings)
        navtb.addAction(settings_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        # Track current downloads
        self.active_downloads = []
        
        # Apply loaded settings
        if self.theme == 'Dark':
            self.set_dark_theme()
        else:
            self.set_light_theme()

    def add_new_tab(self, qurl='https://google.com'):
        browser = QWebEngineView()
        browser.setUrl(QUrl(qurl))

        i = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i: self.tabs.setTabText(i, browser.page().title()))

        # Connect to download signal
        browser.page().profile().downloadRequested.connect(self.handle_download)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def go_back(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().back()

    def go_forward(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().forward()

    def reload_page(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().reload()

    def stop_loading(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().stop()

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.add_new_tab(q)

    def update_urlbar(self, q, browser):
        if browser != self.tabs.currentWidget():
            return

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def navigate_home(self):
        if self.search_engine == "Google":
            self.add_new_tab("https://www.google.com")
        elif self.search_engine == "DuckDuckGo":
            self.add_new_tab("https://duckduckgo.com")
        elif self.search_engine == "Ecosia":
            self.add_new_tab("https://www.ecosia.org")
        else:
            self.add_new_tab("https://www.google.com")

    def handle_download(self, download):
        download.accept()
        download.setPath(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation) + "/" + download.suggestedFileName())
        
        # Track the download
        download_info = {
            'file_name': download.suggestedFileName(),
            'download_item': download
        }
        self.active_downloads.append(download_info)
        
        download.finished.connect(lambda: self.on_download_finished(download))
        download.downloadProgress.connect(self.update_download_progress)

    def on_download_finished(self, download):
        print(f"Download completed: {download.path()}")
        # Remove the download from the active downloads list when done
        self.active_downloads = [d for d in self.active_downloads if d['download_item'] != download]

    def update_download_progress(self, received, total):
        progress = (received / total) * 100 if total > 0 else 0
        print(f"Download progress: {progress}%")

    def show_downloads(self):
        # Show the download window with the list of active downloads
        download_window = DownloadWindow(self.active_downloads, self)
        download_window.exec_()

    def open_settings(self):
        settings_window = SettingsWindow(self)
        settings_window.exec_()

    def set_dark_theme(self):
        self.setStyleSheet("QMainWindow { background-color: #2c2c2c; color: white; }")
        self.tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #444; }")

    def set_light_theme(self):
        self.setStyleSheet("QMainWindow { background-color: #ffffff; color: black; }")
        self.tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #ccc; }")

    def set_search_engine(self, search_engine):
        self.search_engine = search_engine
        print(f"Search engine set to: {search_engine}")


class DownloadWindow(QDialog):
    def __init__(self, downloads, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloads")
        self.setGeometry(600, 200, 400, 300)
        
        self.downloads = downloads
        
        # Layout for the download list
        self.layout = QVBoxLayout()
        
        self.download_list_widget = QListWidget()
        self.layout.addWidget(self.download_list_widget)
        
        self.refresh_downloads()
        
        self.open_folder_btn = QPushButton("Open Download Folder")
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        self.layout.addWidget(self.open_folder_btn)
        
        self.setLayout(self.layout)
    
    def refresh_downloads(self):
        self.download_list_widget.clear()
        for download in self.downloads:
            self.download_list_widget.addItem(download['file_name'])
    
    def open_download_folder(self):
        download_folder = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
        os.startfile(download_folder)


app = QApplication(sys.argv)
app.setApplicationName("Amethystbrowse")
window = MainWindow()
window.show()
app.exec_()

