from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import os
import sys

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Create a new QWebEngineProfile
        profile = QWebEngineProfile()
        # Set the user agent
        profile.setHttpUserAgent(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537')

        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True) # Enable closable tabs
        self.tabs.tabCloseRequested.connect(self.close_tab) # Connect the signal to the slot
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

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

    def add_new_tab(self, qurl='http://google.com'):
        browser = QWebEngineView()
        browser.setUrl(QUrl(qurl))

        i = self.tabs.addTab(browser, "New Tab")
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i: self.tabs.setTabText(i, browser.page().title()))

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
        self.add_new_tab(QUrl("http://www.google.com"))

app = QApplication(sys.argv)
app.setApplicationName("Amethystbrowse")
window = MainWindow()
window.show()
app.exec_()
