# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, 
    QMessageBox, QCheckBox
)
from worker_threads import TestConnectionWorker, LoadModelsWorker

class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setWindowTitle(self.config.tr("dlg_settings"))
        self.resize(600, 500)
        
        self.test_worker = None
        self.load_worker = None

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: API Settings
        self.api_tab = QWidget()
        self._setup_api_tab()
        self.tabs.addTab(self.api_tab, self.config.tr("tab_api"))

        # Tab 2: Prompt Management
        self.prompt_tab = QWidget()
        self._setup_prompt_tab()
        self.tabs.addTab(self.prompt_tab, self.config.tr("tab_prompt"))

        # Tab 3: Accessibility
        self.access_tab = QWidget()
        self._setup_access_tab()
        self.tabs.addTab(self.access_tab, self.config.tr("tab_access"))

        # Tab 4: Exclude Management
        self.exclude_tab = QWidget()
        self._setup_exclude_tab()
        self.tabs.addTab(self.exclude_tab, self.config.tr("tab_exclude"))

        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QPushButton(self.config.tr("btn_save"))
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton(self.config.tr("btn_cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        
    def _setup_api_tab(self):
        layout = QVBoxLayout(self.api_tab)
        
        # Language Selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(self.config.tr("lbl_language")))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("한국어", "ko")
        self.lang_combo.addItem("English", "en")
        idx = self.lang_combo.findData(self.config.get("language", "ko"))
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # API URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel(self.config.tr("lbl_api_url")))
        self.url_input = QLineEdit()
        self.url_input.setText(self.config.get("api_url", ""))
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # API Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel(self.config.tr("lbl_api_key")))
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.Password)
        self.key_input.setText(self.config.get("api_key", ""))
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)

        # Model Configuration
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel(self.config.tr("lbl_select_model")))
        self.model_combo = QComboBox()
        models = self.config.get("models", [])
        if models:
            self.model_combo.addItems(models)
        self.model_combo.setCurrentText(self.config.get("selected_model", ""))
        model_layout.addWidget(self.model_combo)
        
        load_model_btn = QPushButton(self.config.tr("btn_load_model"))
        load_model_btn.clicked.connect(self.load_models)
        model_layout.addWidget(load_model_btn)
        layout.addLayout(model_layout)
        
        # Timeout Configuration
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel(self.config.tr("lbl_timeout")))
        self.timeout_input = QLineEdit()
        self.timeout_input.setText(str(self.config.get("timeout", 30)))
        timeout_layout.addWidget(self.timeout_input)
        timeout_layout.addStretch()
        layout.addLayout(timeout_layout)
        
        # Connection Test
        test_btn = QPushButton(self.config.tr("btn_test_api"))
        test_btn.clicked.connect(self.test_api_connection)
        layout.addWidget(test_btn)
        
        # Terminal Window
        layout.addWidget(QLabel(self.config.tr("lbl_api_resp")))
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: black; color: white; font-family: monospace;")
        layout.addWidget(self.terminal)

    def _setup_prompt_tab(self):
        layout = QVBoxLayout(self.prompt_tab)
        
        # Prompt selection
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel(self.config.tr("lbl_prompt_colon")))
        self.prompt_combo = QComboBox()
        
        self._current_prompts = self.config.get("prompts", {}).copy()
        self._update_prompt_combo()
        self.prompt_combo.setCurrentText(self.config.get("selected_prompt", self.config.tr("default_prompt_name")))
        self.prompt_combo.currentTextChanged.connect(self._on_prompt_combo_changed)
        top_layout.addWidget(self.prompt_combo)
        layout.addLayout(top_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        add_btn = QPushButton(self.config.tr("btn_add"))
        add_btn.clicked.connect(self.add_prompt)
        delete_btn = QPushButton(self.config.tr("btn_delete"))
        delete_btn.clicked.connect(self.delete_prompt)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        
        self.prompt_editor = QTextEdit()
        layout.addWidget(self.prompt_editor)
        self._on_prompt_combo_changed(self.prompt_combo.currentText())

    def _update_prompt_combo(self):
        current_text = self.prompt_combo.currentText()
        self.prompt_combo.clear()
        self.prompt_combo.addItems(list(self._current_prompts.keys()))
        if current_text in self._current_prompts:
            self.prompt_combo.setCurrentText(current_text)

    def _on_prompt_combo_changed(self, text):
        if text in self._current_prompts:
            self.prompt_editor.setText(self._current_prompts[text])

    def add_prompt(self):
        base_name = self.config.tr("prompt_new")
        name = base_name
        counter = 1
        while name in self._current_prompts:
            name = f"{base_name} {counter}"
            counter += 1
            
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, self.config.tr("prompt_add_title"), self.config.tr("prompt_add_msg"), text=name)
        
        if ok and name:
            name = name.strip()
            if not name:
                return
            if name in self._current_prompts:
                QMessageBox.warning(self, self.config.tr("warn_title"), self.config.tr("warn_prompt_exists"))
                return
                
            current_text = self.prompt_combo.currentText()
            if current_text in self._current_prompts:
                self._current_prompts[current_text] = self.prompt_editor.toPlainText()
                
            self._current_prompts[name] = ""
            self._update_prompt_combo()
            self.prompt_combo.setCurrentText(name)

    def delete_prompt(self):
        text = self.prompt_combo.currentText()
        if text == "기본 프롬프트" or text == "Default Prompt":
            QMessageBox.warning(self, self.config.tr("warn_title"), self.config.tr("warn_del_default"))
            return
        
        if text in self._current_prompts:
            del self._current_prompts[text]
            self._update_prompt_combo()

    def _setup_access_tab(self):
        layout = QVBoxLayout(self.access_tab)
        
        self.cb_update_access = QCheckBox(self.config.tr("cb_update_access"))
        self.cb_update_access.setChecked(self.config.get("update_accessibility", False))
        layout.addWidget(self.cb_update_access)
        
        self.access_editor = QTextEdit()
        self.access_editor.setPlainText(self.config.get("accessibility_meta", ""))
        layout.addWidget(self.access_editor)

    def _setup_exclude_tab(self):
        layout = QVBoxLayout(self.exclude_tab)
        
        from PySide6.QtCore import Qt
        
        # 1. 파일명 제외
        file_layout = QHBoxLayout()
        self.cb_exc_file = QCheckBox(self.config.tr("cb_exc_file"))
        self.cb_exc_file.setChecked(self.config.get("exc_filename_enable", False))
        self.txt_exc_file = QTextEdit()
        self.txt_exc_file.setPlainText(self.config.get("exc_filename_val", ""))
        self.txt_exc_file.setPlaceholderText(self.config.tr("ph_exc_file"))
        fm_file = self.txt_exc_file.fontMetrics()
        self.txt_exc_file.setFixedHeight(fm_file.lineSpacing() * 5 + 10)
        file_layout.addWidget(self.cb_exc_file, alignment=Qt.AlignTop)
        file_layout.addWidget(self.txt_exc_file)
        layout.addLayout(file_layout)
        
        # 2. role 제외
        role_layout = QHBoxLayout()
        self.cb_exc_role = QCheckBox(self.config.tr("cb_exc_role"))
        self.cb_exc_role.setChecked(self.config.get("exc_role_enable", False))
        self.txt_exc_role = QTextEdit()
        self.txt_exc_role.setPlainText(self.config.get("exc_role_val", "presentation"))
        self.txt_exc_role.setPlaceholderText(self.config.tr("ph_exc_role"))
        fm_role = self.txt_exc_role.fontMetrics()
        self.txt_exc_role.setFixedHeight(fm_role.lineSpacing() * 5 + 10)
        role_layout.addWidget(self.cb_exc_role, alignment=Qt.AlignTop)
        role_layout.addWidget(self.txt_exc_role)
        layout.addLayout(role_layout)
        
        # 3. size 제외
        size_layout = QHBoxLayout()
        self.cb_exc_size = QCheckBox(self.config.tr("cb_exc_size"))
        self.cb_exc_size.setChecked(self.config.get("exc_size_enable", False))
        size_layout.addWidget(self.cb_exc_size)
        
        size_layout.addWidget(QLabel("Width:"))
        self.txt_exc_w = QLineEdit()
        self.txt_exc_w.setText(self.config.get("exc_size_width", ""))
        self.txt_exc_w.setFixedWidth(60)
        size_layout.addWidget(self.txt_exc_w)
        
        size_layout.addWidget(QLabel("Height:"))
        self.txt_exc_h = QLineEdit()
        self.txt_exc_h.setText(self.config.get("exc_size_height", ""))
        self.txt_exc_h.setFixedWidth(60)
        size_layout.addWidget(self.txt_exc_h)
        size_layout.addWidget(QLabel("px"))
        
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        layout.addStretch()

    def load_models(self):
        if self.load_worker is not None and self.load_worker.isRunning():
            QMessageBox.warning(self, self.config.tr("warn_title"), self.config.tr("warn_loading_models"))
            return

        self.terminal.append(self.config.tr("sys_loading_models"))
        url = self.url_input.text()
        key = self.key_input.text()
        try:
            timeout = int(self.timeout_input.text())
        except ValueError:
            timeout = 30
            
        self.load_worker = LoadModelsWorker(url, key, timeout)
        self.load_worker.finished_signal.connect(self._on_models_loaded)
        self.load_worker.start()
        
    def _on_models_loaded(self, success, models, msg):
        if success:
            self.terminal.append(self.config.tr("load_success"))
            if models:
                self.model_combo.clear()
                self.model_combo.addItems(models)
        else:
            self.terminal.append(self.config.tr("load_fail", msg))

    def _on_test_finished(self, success, resp):
        if success:
            self.terminal.append(self.config.tr("test_success", resp))
        else:
            self.terminal.append(self.config.tr("test_fail", resp))

    def test_api_connection(self):
        if self.test_worker is not None and self.test_worker.isRunning():
            QMessageBox.warning(self, self.config.tr("warn_title"), self.config.tr("warn_testing_conn"))
            return

        model = self.model_combo.currentText()
        if not model:
            QMessageBox.warning(self, self.config.tr("warn_title"), self.config.tr("warn_select_model"))
            return
            
        self.terminal.append(self.config.tr("sys_testing_conn"))
        url = self.url_input.text()
        key = self.key_input.text()
        try:
            timeout = int(self.timeout_input.text())
        except ValueError:
            timeout = 30
        
        self.test_worker = TestConnectionWorker(url, key, timeout, model)
        self.test_worker.finished_signal.connect(self._on_test_finished)
        self.test_worker.start()

    def save_settings(self):
        # Save Language
        self.config.set("language", self.lang_combo.currentData())

        # Save API Settings
        self.config.set("api_url", self.url_input.text())
        self.config.set("api_key", self.key_input.text())
        try:
             self.config.set("timeout", int(self.timeout_input.text()))
        except ValueError:
             self.config.set("timeout", 30)
             
        self.config.set("selected_model", self.model_combo.currentText())
        
        models = [self.model_combo.itemText(i) for i in range(self.model_combo.count())]
        self.config.set("models", models)
        
        current_text = self.prompt_combo.currentText()
        if current_text:
            self._current_prompts[current_text] = self.prompt_editor.toPlainText()

        self.config.set("prompts", self._current_prompts)
        self.config.set("selected_prompt", current_text)
        
        self.config.set("update_accessibility", self.cb_update_access.isChecked())
        self.config.set("accessibility_meta", self.access_editor.toPlainText())

        self.config.set("exc_filename_enable", self.cb_exc_file.isChecked())
        self.config.set("exc_filename_val", self.txt_exc_file.toPlainText())
        self.config.set("exc_role_enable", self.cb_exc_role.isChecked())
        self.config.set("exc_role_val", self.txt_exc_role.toPlainText())
        self.config.set("exc_size_enable", self.cb_exc_size.isChecked())
        self.config.set("exc_size_width", self.txt_exc_w.text())
        self.config.set("exc_size_height", self.txt_exc_h.text())

        self.accept()

    def done(self, r):
        if self.load_worker is not None and self.load_worker.isRunning():
            try:
                self.load_worker.finished_signal.disconnect()
            except Exception:
                pass
            self.load_worker.terminate()
            self.load_worker.wait()
            
        if self.test_worker is not None and self.test_worker.isRunning():
            try:
                self.test_worker.finished_signal.disconnect()
            except Exception:
                pass
            self.test_worker.terminate()
            self.test_worker.wait()
            
        super().done(r)