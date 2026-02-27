from google.cloud import translate_v3 as translate
import streamlit as st


class GCTranslateUtils:
    def __init__(self):
        self._project_id = st.secrets["gc_project_id"]

    def get_supported_languages(self, display_language_code="en"):
        client = translate.TranslationServiceClient()

        response = client.get_supported_languages(
            parent=f"projects/{self._project_id}",
            display_language_code=display_language_code,
        )

        languages = response.languages  
        # for language in languages:
        #     language_code = language.language_code
        #     display_name = language.display_name
        return languages

    def translateText(self, text, src_lang_code="en", tgt_lang_code="ko"):
        client = translate.TranslationServiceClient()
        parent = f"projects/{self._project_id}/locations/global"
        response = client.translate_text(
            parent=parent,
            contents=[text],
            source_language_code=src_lang_code,
            target_language_code=tgt_lang_code,
        )

        meaning_kr = ", ".join([t.translated_text for t in response.translations])
        return meaning_kr