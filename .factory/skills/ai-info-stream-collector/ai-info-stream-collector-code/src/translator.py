import time
from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

class ArticleTranslator:
    def __init__(self, target_lang='zh-CN'):
        self.target_lang = target_lang
        self.translator = GoogleTranslator(source='auto', target=target_lang)
        self.cache = {}
        
    def translate(self, text, retry=3):
        if not text or text.strip() == "":
            return text
            
        if text in self.cache:
            return self.cache[text]
        
        for attempt in range(retry):
            try:
                translated = self.translator.translate(text)
                self.cache[text] = translated
                time.sleep(0.5)
                return translated
            except Exception as e:
                logger.warning(f"Translation attempt {attempt + 1} failed: {e}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to translate after {retry} attempts: {text[:50]}...")
                    return text
        
        return text
