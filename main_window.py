# -*- coding: utf-8 -*-
import sys
import posixpath
import urllib.parse
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLabel, QTextEdit, QPushButton,
    QComboBox, QMessageBox, QProgressDialog, QSplitter, QDialog,
    QScrollArea
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QSize, QByteArray

from config import ConfigManager
from epub_processor import EpubProcessor
from settings_dialog import SettingsDialog
from worker_threads import GenerateAltWorker

class DraggableLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        try:
            open_cursor = getattr(Qt, "OpenHandCursor", getattr(Qt.CursorShape, "OpenHandCursor", 17))
            self.setCursor(open_cursor)
        except Exception:
            pass
        self._is_panning = False
        self._start_pos = None
        self.scroll_area_ref = None

    def _get_pos(self, event):
        try:
            if hasattr(event, "globalPosition"):
                return event.globalPosition().toPoint()
            elif hasattr(event, "globalPos"):
                return event.globalPos()
            else:
                return event.pos()
        except Exception:
            return event.pos()

    def mousePressEvent(self, event):
        try:
            if event.button() == getattr(Qt, "LeftButton", getattr(Qt.MouseButton, "LeftButton", 1)):
                self._is_panning = True
                self._start_pos = self._get_pos(event)
                try:
                    closed_cursor = getattr(Qt, "ClosedHandCursor", getattr(Qt.CursorShape, "ClosedHandCursor", 18))
                    self.setCursor(closed_cursor)
                except Exception:
                    pass
        except Exception:
            pass
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        try:
            if self._is_panning and self._start_pos is not None:
                current_pos = self._get_pos(event)
                delta = current_pos - self._start_pos
                self._start_pos = current_pos
                
                if self.scroll_area_ref:
                    h_bar = self.scroll_area_ref.horizontalScrollBar()
                    v_bar = self.scroll_area_ref.verticalScrollBar()
                    h_bar.setValue(h_bar.value() - delta.x())
                    v_bar.setValue(v_bar.value() - delta.y())
        except Exception:
            pass
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == getattr(Qt, "LeftButton", getattr(Qt.MouseButton, "LeftButton", 1)):
                self._is_panning = False
                try:
                    open_cursor = getattr(Qt, "OpenHandCursor", getattr(Qt.CursorShape, "OpenHandCursor", 17))
                    self.setCursor(open_cursor)
                except Exception:
                    pass
        except Exception:
            pass
        super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):
    def __init__(self, bk):
        super().__init__()
        self.bk = bk
        self.config = ConfigManager(bk)
        self.processor = EpubProcessor(bk)
        self.images_info = []
        self.excluded_images_info = []
        self.workers = {} 
        self.current_processing_index = -1
        self.processing_all = False
        self.zoom_factor = 1.0
        self.current_pixmap = None

        self.setWindowTitle(self.config.tr("window_title"))
        win_size = self.config.get("window_size", [900, 600])
        self.resize(win_size[0], win_size[1])
        self._init_ui()
        self.load_images()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # ---------------- Top Bar ----------------
        top_bar = QHBoxLayout()
        
        self.btn_gen_all = QPushButton(self.config.tr("btn_gen_all"))
        self.btn_gen_all.clicked.connect(self.generate_all_alt)
        top_bar.addWidget(self.btn_gen_all)
        
        top_bar.addWidget(QLabel(self.config.tr("lbl_prompt")))
        self.prompt_combo = QComboBox()
        self.prompt_combo.addItems(list(self.config.get("prompts", {}).keys()))
        selected_prompt = self.config.get("selected_prompt", self.config.tr("default_prompt_name"))
        self.prompt_combo.setCurrentText(selected_prompt)
        self.prompt_combo.currentTextChanged.connect(self._on_prompt_changed)
        top_bar.addWidget(self.prompt_combo)
        
        top_bar.addWidget(QLabel(self.config.tr("lbl_model")))
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.config.get("models", []))
        selected_model = self.config.get("selected_model", "")
        if selected_model:
            self.model_combo.setCurrentText(selected_model)
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        top_bar.addWidget(self.model_combo)
        
        top_bar.addStretch()
        
        self.btn_settings = QPushButton(self.config.tr("btn_settings"))
        self.btn_settings.clicked.connect(self.open_settings)
        top_bar.addWidget(self.btn_settings)
        
        self.btn_apply = QPushButton(self.config.tr("btn_apply"))
        self.btn_apply.clicked.connect(self.apply_and_close)
        top_bar.addWidget(self.btn_apply)
        
        main_layout.addLayout(top_bar)

        # ---------------- Splitter ----------------
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter, stretch=1)

        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(100, 100))
        self.list_widget.itemSelectionChanged.connect(self._on_item_selected)
        left_layout.addWidget(self.list_widget)

        self.lbl_counter = QLabel("0 / 0")
        self.lbl_counter.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.lbl_counter)
        
        self.splitter.addWidget(left_panel)

        # Right Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_top_bar = QHBoxLayout()
        right_top_bar.addWidget(QLabel(self.config.tr("lbl_role")))
        self.role_combo = QComboBox()
        self.role_combo.addItems(self.config.get("roles", ["img", "cover", "presentation"]))
        self.role_combo.currentTextChanged.connect(self._on_role_changed)
        right_top_bar.addWidget(self.role_combo)
        
        right_top_bar.addStretch()
        
        self.btn_gen_current = QPushButton(self.config.tr("btn_gen_current"))
        self.btn_gen_current.clicked.connect(self.generate_current_alt)
        right_top_bar.addWidget(self.btn_gen_current)
        
        right_layout.addLayout(right_top_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setMinimumSize(300, 300)
        self.scroll_area.setStyleSheet("QScrollArea { border: 1px solid #ccc; }")
        
        self.lbl_preview = DraggableLabel(self.config.tr("lbl_select_image"))
        self.lbl_preview.scroll_area_ref = self.scroll_area
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.wheelEvent = self._on_preview_wheel
        self.scroll_area.setWidget(self.lbl_preview)
        
        right_layout.addWidget(self.scroll_area, stretch=2)

        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel(self.config.tr("lbl_img_desc")))
        desc_layout.addStretch()
        
        self.btn_zoom_out = QPushButton("-")
        self.btn_zoom_out.setFixedSize(30, 30)
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        desc_layout.addWidget(self.btn_zoom_out)
        
        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setFixedSize(30, 30)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        desc_layout.addWidget(self.btn_zoom_in)
        
        right_layout.addLayout(desc_layout)

        self.txt_alt = QTextEdit()
        self.txt_alt.textChanged.connect(self._on_alt_changed)
        right_layout.addWidget(self.txt_alt, stretch=1)

        self.splitter.addWidget(right_panel)
        
        splitter_sizes = self.config.get("splitter_sizes", [200, 700])
        self.splitter.setSizes(splitter_sizes)

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.update_preview_image()
        
    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.update_preview_image()

    def _on_preview_wheel(self, event):
        angle = event.angleDelta().y()
        if angle > 0:
            self.zoom_in()
        elif angle < 0:
            self.zoom_out()
        event.accept()

    def update_preview_image(self):
        if not self.current_pixmap or self.current_pixmap.isNull():
            return
            
        container_size = self.scroll_area.size() - QSize(4, 4)
        base_pixmap = self.current_pixmap.scaled(
            container_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        target_width = int(base_pixmap.width() * self.zoom_factor)
        target_height = int(base_pixmap.height() * self.zoom_factor)
        
        final_pixmap = self.current_pixmap.scaled(
            target_width, target_height,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.lbl_preview.setPixmap(final_pixmap)

    def _is_excluded(self, info, pixmap):
        if self.config.get("exc_filename_enable", False):
            exc_val = self.config.get("exc_filename_val", "")
            if exc_val:
                src_clean = urllib.parse.unquote(info.get("src", "").split('#')[0])
                filename = posixpath.basename(src_clean)
                display_name, _ = posixpath.splitext(filename)
                
                exc_val = exc_val.replace('\n', ',')
                patterns = [p.strip() for p in exc_val.split(',') if p.strip()]
                import re
                for p in patterns:
                    regex = "^" + re.escape(p).replace("\\*", ".*") + "$"
                    if re.match(regex, display_name, re.IGNORECASE):
                        return True

        if self.config.get("exc_role_enable", False):
            exc_val = self.config.get("exc_role_val", "")
            if exc_val:
                exc_val = exc_val.replace('\n', ',')
                roles = [r.strip() for r in exc_val.split(',') if r.strip()]
                if info.get("role", "") in roles:
                    return True

        if self.config.get("exc_size_enable", False) and pixmap and not pixmap.isNull():
            w_str = self.config.get("exc_size_width", "").strip()
            h_str = self.config.get("exc_size_height", "").strip()
            
            try:
                w_limit = int(w_str) if w_str else 0
            except ValueError:
                w_limit = 0
                
            try:
                h_limit = int(h_str) if h_str else 0
            except ValueError:
                h_limit = 0
                
            if w_limit > 0 and pixmap.width() < w_limit:
                return True
            if h_limit > 0 and pixmap.height() < h_limit:
                return True
                
        return False

    def load_images(self):
        raw_images_info = self.processor.extract_images_from_text()
        self.images_info = []
        self.excluded_images_info = []
        self.list_widget.clear()
        
        idx_counter = 0
        for info in raw_images_info:
            raw_data = self.processor.get_image_data(info["img_id"])
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(raw_data))
            
            if self._is_excluded(info, pixmap):
                self.excluded_images_info.append(info)
                continue
                
            self.images_info.append(info)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon = QIcon(scaled_pixmap)
            
            src_clean = urllib.parse.unquote(info.get("src", "").split('#')[0])
            filename = posixpath.basename(src_clean)
            display_name, _ = posixpath.splitext(filename)
            if not display_name:
                display_name = f"Img {idx_counter+1}"
                
            item = QListWidgetItem(icon, display_name)
            item.setData(Qt.UserRole, idx_counter)
            self.list_widget.addItem(item)
            idx_counter += 1
            
        self._update_counter()
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
        else:
            self.lbl_preview.setText(self.config.tr("msg_no_image"))
            self.lbl_preview.setPixmap(QPixmap())
            self.txt_alt.clear()

    def _update_counter(self):
        current = self.list_widget.currentRow() + 1
        total = self.list_widget.count()
        if total == 0:
            current = 0
        self.lbl_counter.setText(f"{current} / {total}")

    def _on_item_selected(self):
        self._update_counter()
        items = self.list_widget.selectedItems()
        if not items:
            return
        
        idx = items[0].data(Qt.UserRole)
        info = self.images_info[idx]
        
        raw_data = self.processor.get_image_data(info["img_id"])
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(raw_data))
        
        self.current_pixmap = pixmap
        self.zoom_factor = 1.0
        self.update_preview_image()
        
        self.txt_alt.blockSignals(True)
        self.txt_alt.setText(info["alt"])
        self.txt_alt.blockSignals(False)
        
        self.role_combo.blockSignals(True)
        self.role_combo.setCurrentText(info["role"])
        self.role_combo.blockSignals(False)

    def _on_alt_changed(self):
        items = self.list_widget.selectedItems()
        if not items: return
        idx = items[0].data(Qt.UserRole)
        self.images_info[idx]["alt"] = self.txt_alt.toPlainText()

    def _on_role_changed(self, text):
        items = self.list_widget.selectedItems()
        if not items: return
        idx = items[0].data(Qt.UserRole)
        self.images_info[idx]["role"] = text

    def open_settings(self):
        dlg = SettingsDialog(self.config, self)
        if dlg.exec() == QDialog.Accepted:
            
            roles = self.config.get("roles", ["img", "cover", "presentation"])
            current_role = self.role_combo.currentText()
            self.role_combo.blockSignals(True)
            self.role_combo.clear()
            self.role_combo.addItems(roles)
            if current_role in roles:
                self.role_combo.setCurrentText(current_role)
            self.role_combo.blockSignals(False)
            
            models = self.config.get("models", [])
            current_model = self.config.get("selected_model", "")
            self.model_combo.blockSignals(True)
            self.model_combo.clear()
            self.model_combo.addItems(models)
            if current_model in models:
                self.model_combo.setCurrentText(current_model)
            elif models:
                self.model_combo.setCurrentText(models[0])
            self.model_combo.blockSignals(False)

            prompts = list(self.config.get("prompts", {}).keys())
            current_prompt = self.config.get("selected_prompt", self.config.tr("default_prompt_name"))
            self.prompt_combo.blockSignals(True)
            self.prompt_combo.clear()
            self.prompt_combo.addItems(prompts)
            if current_prompt in prompts:
                self.prompt_combo.setCurrentText(current_prompt)
            elif prompts:
                self.prompt_combo.setCurrentText(prompts[0])
            self.prompt_combo.blockSignals(False)
            
            self.setWindowTitle(self.config.tr("window_title"))
            self.btn_gen_all.setText(self.config.tr("btn_gen_all"))
            self.btn_settings.setText(self.config.tr("btn_settings"))
            self.btn_apply.setText(self.config.tr("btn_apply"))
            self.btn_gen_current.setText(self.config.tr("btn_gen_current"))

            self.load_images()

    def _on_prompt_changed(self, text):
        self.config.set("selected_prompt", text)
        
    def _on_model_changed(self, text):
        self.config.set("selected_model", text)

    def generate_current_alt(self):
        items = self.list_widget.selectedItems()
        if not items:
            QMessageBox.warning(self, self.config.tr("warn_title"), self.config.tr("warn_select_first"))
            return
        idx = items[0].data(Qt.UserRole)
        self._start_generation(idx)

    def generate_all_alt(self):
        if not self.images_info: return
        
        reply = QMessageBox.question(self, self.config.tr("gen_all_title"), self.config.tr("gen_all_msg"), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return
        
        self.processing_all = True
        self.current_processing_index = 0
        self._set_ui_enabled(False)
        self.list_widget.setCurrentRow(self.current_processing_index)
        self._start_generation(self.current_processing_index)

    def _start_generation(self, idx):
        if str(idx) in self.workers and self.workers[str(idx)].isRunning():
            if not self.processing_all:
                QMessageBox.warning(self, self.config.tr("warn_title"), self.config.tr("warn_in_progress"))
            return

        info = self.images_info[idx]
        prompt_name = self.prompt_combo.currentText()
        prompts = self.config.get("prompts", {})
        prompt_text = prompts.get(prompt_name, "")
        
        api_url = self.config.get("api_url", "")
        model = self.model_combo.currentText()
        if not model:
            model = self.config.get("selected_model", "")
            
        api_key = self.config.get("api_key", "")
        timeout = self.config.get("timeout", 30)

        if not api_url or not model:
            QMessageBox.warning(self, self.config.tr("err_title"), self.config.tr("err_settings"))
            self.processing_all = False
            self._set_ui_enabled(True)
            return

        raw_data = self.processor.get_image_data(info["img_id"])
        
        self.txt_alt.blockSignals(True)
        self.txt_alt.setText(self.config.tr("msg_generating"))
        self.txt_alt.blockSignals(False)

        worker = GenerateAltWorker(api_url, api_key, timeout, model, prompt_text, raw_data, str(idx))
        worker.finished_signal.connect(self._on_generation_finished)
        worker.error_signal.connect(self._on_generation_error)
        self.workers[str(idx)] = worker
        worker.start()
        
    def _on_generation_finished(self, idx_str, result_text):
        idx = int(idx_str)
        self.images_info[idx]["alt"] = result_text
        if str(idx) in self.workers:
            del self.workers[str(idx)]
            
        items = self.list_widget.selectedItems()
        if items and items[0].data(Qt.UserRole) == idx:
            self.txt_alt.blockSignals(True)
            self.txt_alt.setText(result_text)
            self.txt_alt.blockSignals(False)
            
        self._continue_or_finish()

    def _on_generation_error(self, idx_str, err_msg):
        idx = int(idx_str)
        if str(idx) in self.workers:
            del self.workers[str(idx)]
            
        self.images_info[idx]["alt"] += f"\n{self.config.tr('err_occurred')}: {err_msg}"
        
        items = self.list_widget.selectedItems()
        if items and items[0].data(Qt.UserRole) == idx:
            self.txt_alt.blockSignals(True)
            self.txt_alt.setText(self.images_info[idx]["alt"])
            self.txt_alt.blockSignals(False)
            
        QMessageBox.warning(self, self.config.tr("err_gen_title"), self.config.tr("err_gen_msg", idx+1, err_msg))
        self.processing_all = False
        self._set_ui_enabled(True)

    def _continue_or_finish(self):
        if self.processing_all:
            self.current_processing_index += 1
            if self.current_processing_index < len(self.images_info):
                self.list_widget.setCurrentRow(self.current_processing_index)
                self._start_generation(self.current_processing_index)
            else:
                self.processing_all = False
                self._set_ui_enabled(True)
                QMessageBox.information(self, self.config.tr("info_done_title"), self.config.tr("info_done_msg"))
        else:
            self._set_ui_enabled(True)

    def _set_ui_enabled(self, enabled):
        self.btn_gen_all.setEnabled(enabled)
        self.btn_gen_current.setEnabled(enabled)
        self.btn_settings.setEnabled(enabled)
        self.btn_apply.setEnabled(enabled)
        self.list_widget.setEnabled(enabled)
        self.btn_zoom_in.setEnabled(enabled)
        self.btn_zoom_out.setEnabled(enabled)
        self.txt_alt.setReadOnly(not enabled)

    def apply_and_close(self):
        update_meta = self.config.get("update_accessibility", False)
        meta_text = self.config.get("accessibility_meta", "")
        
        final_images = self.images_info.copy()
        for exc_info in self.excluded_images_info:
            exc_info["role"] = "presentation"
            final_images.append(exc_info)
            
        self.processor.apply_to_epub(final_images, update_meta, meta_text)
        self.close()

    def closeEvent(self, event):
        for worker in list(self.workers.values()):
            if worker.isRunning():
                try:
                    worker.finished_signal.disconnect()
                    worker.error_signal.disconnect()
                except Exception:
                    pass
                worker.terminate()
                worker.wait()

        self.config.set("window_size", [self.width(), self.height()])
        self.config.set("splitter_sizes", self.splitter.sizes())
        super().closeEvent(event)

def launch_gui(bk):
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        window = MainWindow(bk)
        window.show()
        
        app.exec()
        return 0
    except Exception as e:
        import traceback
        import os
        log_path = os.path.join(os.path.dirname(__file__), "crash_log.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise