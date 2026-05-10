# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.error
import base64

class LLMClient:
    def __init__(self, api_url, api_key=None, timeout=30):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout

    def _make_request(self, endpoint, payload=None, method="POST"):
        url = self.api_url + endpoint
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = None
        if payload is not None:
            data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = response.read().decode('utf-8')
                return json.loads(result)
        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError):
                raise Exception("응답 시간 초과")
            raise Exception(str(e))
        except Exception as e:
            raise Exception(str(e))

    def fetch_models(self):
        # Support OpenAI compatible endpoint
        try:
            resp = self._make_request("/models", method="GET")
            if "data" in resp:
                return [m["id"] for m in resp["data"]]
            elif "models" in resp:
                return [m["name"] for m in resp["models"]]
            return []
        except Exception:
            # Fallback to Ollama native /api/tags if /v1/models fails and url is /api related
            try:
                base_url = self.api_url.replace("/v1", "/api")
                url = base_url + "/tags"
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    return [m["name"] for m in result.get("models", [])]
            except Exception as e2:
                raise Exception("모델을 불러오지 못했습니다. 에러: " + str(e2))

    def test_connection(self, model):
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        resp = self._make_request("/chat/completions", payload=payload)
        if "choices" in resp and len(resp["choices"]) > 0:
            return resp["choices"][0]["message"]["content"]
        elif "message" in resp:
            # Maybe ollama native /api/chat
            return resp["message"]["content"]
        raise Exception("예상치 못한 응답 형식입니다.")

    def generate_alt(self, model, prompt, image_data):
        b64_image = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1024
        }
        
        resp = self._make_request("/chat/completions", payload=payload)
        try:
            return resp["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            # Check if it has 'message' instead (native ollama chat response)
            if "message" in resp and "content" in resp["message"]:
                return resp["message"]["content"].strip()
            raise Exception("올바른 응답을 받지 못했습니다.")

