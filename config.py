# -*- coding: utf-8 -*-
import os
import locale

DEFAULT_PROMPT_KO = """이미지에 대해 상세히 묘사.
**Rule**
- 표지 이미지는 표지에 있는 **텍스트를 순서대로 모두 표시**하며, 표지의 텍스트 이외에 다른 설명은 절대로 추가하지 않아야 함.

- 이미지에 대해 상세히 설명해야 하며, **반드시** 설명 끝에 "그림", "사진", "도표", "표"로 그림 형식을 표시. **이 규칙은 표지에 적용하지 않음**
예) 초원에 뛰어다니는 토기를 묘사한 그림
예)10년간 주식 시세를 그린 도표
- 표, 도표, 그래프는 이미지에서 강조하고자 하는 내용을 중심으로 설명함
- 그 외 사진, 그림 등은 어떤 이미지인지 알 수 있도록 간략히 묘사."""

DEFAULT_PROMPT_EN = """Describe the image in detail.
**Rule**
- For cover images, **display all text on the cover in order**, and never add any other description besides the text on the cover.

- Describe the image in detail, and **must** indicate the image format at the end of the description with "drawing", "photograph", "chart", or "table". **This rule does not apply to the cover**
Ex) A drawing depicting a rabbit running in a meadow
Ex) A chart showing stock prices over 10 years
- For tables, charts, and graphs, focus the description on the content to be highlighted in the image
- For other photos, drawings, etc., describe them briefly so that it is clear what the image is."""

I18N = {
    "window_title": {"ko": "Image Alt Generator", "en": "Image Alt Generator"},
    "btn_gen_all": {"ko": "Alt 생성", "en": "Generate Alt"},
    "lbl_prompt": {"ko": "프롬프트 :", "en": "Prompt :"},
    "default_prompt_name": {"ko": "기본 프롬프트", "en": "Default Prompt"},
    "lbl_model": {"ko": "모델 :", "en": "Model :"},
    "btn_settings": {"ko": "설정", "en": "Settings"},
    "btn_apply": {"ko": "EPUB에 적용", "en": "Apply to EPUB"},
    "lbl_role": {"ko": "role :", "en": "Role :"},
    "btn_gen_current": {"ko": "다시 생성", "en": "Regenerate"},
    "msg_no_image": {"ko": "조회된 이미지가 없습니다.", "en": "No images found."},
    "lbl_select_image": {"ko": "이미지를 선택하세요", "en": "Select an image"},
    "lbl_img_desc": {"ko": "이미지 설명:", "en": "Image Description:"},
    "warn_title": {"ko": "경고", "en": "Warning"},
    "warn_select_first": {"ko": "이미지를 먼저 선택하세요.", "en": "Please select an image first."},
    "gen_all_title": {"ko": "전체 생성", "en": "Generate All"},
    "gen_all_msg": {"ko": "모든 이미지의 설명을 생성하시겠습니까?", "en": "Do you want to generate descriptions for all images?"},
    "warn_in_progress": {"ko": "해당 이미지는 이미 작업이 진행 중입니다.", "en": "This image is already being processed."},
    "err_settings": {"ko": "설정에서 API URL과 모델을 먼저 설정하세요.", "en": "Please configure API URL and Model in Settings first."},
    "err_title": {"ko": "설정 오류", "en": "Settings Error"},
    "msg_generating": {"ko": "생성 중입니다...", "en": "Generating..."},
    "err_occurred": {"ko": "에러 발생", "en": "Error occurred"},
    "err_gen_title": {"ko": "생성 오류", "en": "Generation Error"},
    "err_gen_msg": {"ko": "이미지 {0} 처리 중 오류 발생: {1}\n작업을 중단합니다.", "en": "Error processing image {0}: {1}\nTask aborted."},
    "info_done_title": {"ko": "완료", "en": "Done"},
    "info_done_msg": {"ko": "모든 이미지의 설명을 생성했습니다.", "en": "Generated descriptions for all images."},
    
    "dlg_settings": {"ko": "설정", "en": "Settings"},
    "tab_api": {"ko": "API 설정", "en": "API Settings"},
    "tab_prompt": {"ko": "프롬프트 관리", "en": "Prompt Mgmt"},
    "tab_access": {"ko": "접근성 관리", "en": "Accessibility"},
    "tab_exclude": {"ko": "제외 관리", "en": "Exclusion"},
    "btn_save": {"ko": "저장", "en": "Save"},
    "btn_cancel": {"ko": "취소", "en": "Cancel"},
    "lbl_language": {"ko": "언어 (Language):", "en": "Language:"},
    "lbl_api_url": {"ko": "API URL:", "en": "API URL:"},
    "lbl_api_key": {"ko": "API Key:", "en": "API Key:"},
    "lbl_select_model": {"ko": "모델 선택:", "en": "Select Model:"},
    "btn_load_model": {"ko": "[불러오기]", "en": "[Load]"},
    "lbl_timeout": {"ko": "연결 대기 시간(초):", "en": "Timeout (sec):"},
    "btn_test_api": {"ko": "API 연동 확인", "en": "Test API Conn"},
    "lbl_api_resp": {"ko": "연동 메시지 응답:", "en": "API Response:"},
    "lbl_prompt_colon": {"ko": "프롬프트:", "en": "Prompt:"},
    "btn_add": {"ko": "추가", "en": "Add"},
    "btn_delete": {"ko": "삭제", "en": "Delete"},
    "prompt_new": {"ko": "새 프롬프트", "en": "New Prompt"},
    "prompt_add_title": {"ko": "프롬프트 추가", "en": "Add Prompt"},
    "prompt_add_msg": {"ko": "새 프롬프트 이름을 입력하세요:", "en": "Enter new prompt name:"},
    "warn_prompt_exists": {"ko": "이미 존재하는 프롬프트 이름입니다.", "en": "Prompt name already exists."},
    "warn_del_default": {"ko": "기본 프롬프트는 삭제할 수 없습니다.", "en": "Default prompt cannot be deleted."},
    "cb_update_access": {"ko": "EPUB3 파일에 opf에 접근성 메타 정보를 업데이트", "en": "Update accessibility meta info in EPUB3 opf"},
    "cb_exc_file": {"ko": "파일명 제외:", "en": "Exclude Filename:"},
    "ph_exc_file": {"ko": "여러 줄 입력 혹은 콤마(,) 구분 가능\n예) bullet, chap*, box*, line", "en": "Multiple lines or comma separated\nEx) bullet, chap*, box*, line"},
    "cb_exc_role": {"ko": "role 제외:", "en": "Exclude Role:"},
    "ph_exc_role": {"ko": "여러 줄 입력 혹은 콤마(,) 구분 가능\n예) presentation, none", "en": "Multiple lines or comma separated\nEx) presentation, none"},
    "cb_exc_size": {"ko": "size 제외:", "en": "Exclude Size:"},
    "warn_loading_models": {"ko": "이미 모델 목록을 불러오는 중입니다.", "en": "Already loading models."},
    "sys_loading_models": {"ko": "[시스템] 모델 목록 불러오는 중...", "en": "[System] Loading models..."},
    "warn_select_model": {"ko": "모델을 먼저 선택/입력해주세요.", "en": "Please select/enter a model first."},
    "sys_testing_conn": {"ko": "[시스템] 연결 확인 중...", "en": "[System] Testing connection..."},
    "warn_testing_conn": {"ko": "이미 연결을 확인 중입니다.", "en": "Already testing connection."},
    "test_success": {"ko": "결과: 연결 성공! 응답: {0}", "en": "Result: Connection successful! Response: {0}"},
    "test_fail": {"ko": "결과: 연결 실패: {0}", "en": "Result: Connection failed: {0}"},
    "load_success": {"ko": "[시스템] 모델 불러오기 성공", "en": "[System] Models loaded successfully"},
    "load_fail": {"ko": "[시스템] {0}", "en": "[System] {0}"}
}

def get_sys_lang():
    lang = os.environ.get('LANG', '')
    if lang.startswith('ko'): return 'ko'
    try:
        if hasattr(locale, 'getdefaultlocale'):
            loc = locale.getdefaultlocale()[0]
        else:
            loc = locale.getlocale()[0]
        if loc and loc.startswith('ko'): return 'ko'
    except: pass
    try:
        import ctypes
        if os.name == 'nt':
            if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF == 0x12:
                return 'ko'
    except: pass
    return 'en'

class ConfigManager:
    def __init__(self, bk):
        self.bk = bk
        self.prefs = bk.getPrefs() if bk is not None else {}
        self._ensure_defaults()

    def tr(self, key, *args):
        lang = self.get("language", "en")
        text = I18N.get(key, {}).get(lang, key)
        if args:
            try:
                return text.format(*args)
            except Exception:
                pass
        return text

    def _ensure_defaults(self):
        updated = False
        
        # 언어 기본값 지정 (최초 실행 시 시스템 언어 감지)
        if "language" not in self.prefs:
            self.prefs["language"] = get_sys_lang()
            updated = True
            
        lang = self.prefs["language"]
        default_prompt_name = "기본 프롬프트" if lang == "ko" else "Default Prompt"
        default_prompt_content = DEFAULT_PROMPT_KO if lang == "ko" else DEFAULT_PROMPT_EN

        if "api_url" not in self.prefs:
            self.prefs["api_url"] = "http://localhost:11434/v1"
            updated = True
        if "api_key" not in self.prefs:
            self.prefs["api_key"] = ""
            updated = True
        if "timeout" not in self.prefs:
            self.prefs["timeout"] = 30
            updated = True
        if "models" not in self.prefs:
            self.prefs["models"] = []
            updated = True
        if "selected_model" not in self.prefs:
            self.prefs["selected_model"] = ""
            updated = True
            
        if "prompts" not in self.prefs:
            self.prefs["prompts"] = {
                default_prompt_name: default_prompt_content
            }
            updated = True
        elif "기본 프롬프트" not in self.prefs["prompts"] and "Default Prompt" not in self.prefs["prompts"]:
            # 설정 파일에 기본 프롬프트가 없을 경우 해당 언어에 맞춰 추가 등록
            self.prefs["prompts"][default_prompt_name] = default_prompt_content
            updated = True
            
        if "selected_prompt" not in self.prefs:
            self.prefs["selected_prompt"] = default_prompt_name
            updated = True
            
        if "roles" not in self.prefs:
            self.prefs["roles"] = ["img", "cover", "presentation"]
            updated = True
            
        if "accessibility_meta" not in self.prefs:
            self.prefs["accessibility_meta"] = ""
            updated = True
        if "update_accessibility" not in self.prefs:
            self.prefs["update_accessibility"] = False
            updated = True

        if "exc_filename_enable" not in self.prefs:
            self.prefs["exc_filename_enable"] = False
            updated = True
        if "exc_filename_val" not in self.prefs:
            self.prefs["exc_filename_val"] = ""
            updated = True
            
        if "exc_role_enable" not in self.prefs:
            self.prefs["exc_role_enable"] = False
            updated = True
        if "exc_role_val" not in self.prefs:
            self.prefs["exc_role_val"] = "presentation"
            updated = True
            
        if "exc_size_enable" not in self.prefs:
            self.prefs["exc_size_enable"] = False
            updated = True
        if "exc_size_width" not in self.prefs:
            self.prefs["exc_size_width"] = ""
            updated = True
        if "exc_size_height" not in self.prefs:
            self.prefs["exc_size_height"] = ""
            updated = True

        if updated:
            self.save()

    def save(self):
        if self.bk is not None:
            self.bk.savePrefs(self.prefs)

    def get(self, key, default=None):
        return self.prefs.get(key, default)

    def set(self, key, value):
        self.prefs[key] = value
        self.save()