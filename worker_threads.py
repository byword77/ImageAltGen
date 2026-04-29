# -*- coding: utf-8 -*-
from PySide6.QtCore import QThread, Signal
from llm_client import LLMClient

class TestConnectionWorker(QThread):
    finished_signal = Signal(bool, str)

    def __init__(self, api_url, api_key, timeout, model):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.model = model

    def run(self):
        try:
            client = LLMClient(self.api_url, self.api_key, self.timeout)
            resp = client.test_connection(self.model)
            # 순수 결과만 UI로 전달
            self.finished_signal.emit(True, str(resp))
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class LoadModelsWorker(QThread):
    finished_signal = Signal(bool, list, str)

    def __init__(self, api_url, api_key, timeout):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    def run(self):
        try:
            client = LLMClient(self.api_url, self.api_key, self.timeout)
            models = client.fetch_models()
            self.finished_signal.emit(True, models, "")
        except Exception as e:
            self.finished_signal.emit(False, [], str(e))


class GenerateAltWorker(QThread):
    finished_signal = Signal(str, str) # current image hash or id, result text or error message
    error_signal = Signal(str, str)

    def __init__(self, api_url, api_key, timeout, model, prompt, image_data, current_id):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.model = model
        self.prompt = prompt
        self.image_data = image_data
        self.current_id = current_id

    def run(self):
        try:
            client = LLMClient(self.api_url, self.api_key, self.timeout)
            alt_text = client.generate_alt(self.model, self.prompt, self.image_data)
            self.finished_signal.emit(self.current_id, alt_text)
        except Exception as e:
            self.error_signal.emit(self.current_id, str(e))