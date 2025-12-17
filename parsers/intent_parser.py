import re
from typing import Dict, Optional
from datetime import datetime

class IntentParser:
    """Parse user messages into structured intents"""
    
    PATTERNS = {
        "PRODUCT_SEARCH": [
            r"find\s+(.+?)\s+(?:on|in)\s+(.+)",
            r"search\s+(?:for\s+)?(.+?)\s+(?:on|in)\s+(.+)",
            r"look\s+(?:for\s+)?(.+?)\s+(?:on|in)\s+(.+)"
        ],
        "MEDIA_GENERATION": [
            r"generate\s+(?:a|an)\s+(.+)",
            r"create\s+(?:a|an)\s+(.+)",
            r"make\s+(?:a|an)\s+(.+)"
        ],
        "REMINDER": [
            r"remind\s+me\s+to\s+(.+?)\s+(?:at|on|every|in)\s+(.+)",
            r"set\s+(?:a\s+)?reminder\s+(?:to\s+)?(.+?)\s+(?:at|on|every|in)\s+(.+)"
        ],
        "MEMORY_STORE": [
            r"remember\s+(.+)",
            r"save\s+(?:this\s+)?(?:info|information):\s*(.+)",
            r"store\s+(.+)",
            r"note\s+(?:that\s+)?(.+)"
        ]
    }
    
    MEDIA_TYPES = {
        "image": ["image", "picture", "photo", "illustration", "drawing"],
        "video": ["video", "clip", "animation", "movie"],
        "audio": ["audio", "sound", "music", "song"],
        "voice": ["voice", "speech", "narration"]
    }
    
    def parse(self, message: str) -> Dict:
        """Parse message into intent structure"""
        message = message.strip().lower()
        
        for intent_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    return self._build_intent(intent_type, match, message)
        
        return {
            "type": "GENERAL_QUERY",
            "message": message,
            "confidence": 0.5
        }
    
    def _build_intent(self, intent_type: str, match, original_message: str) -> Dict:
        """Build structured intent from regex match"""
        
        if intent_type == "PRODUCT_SEARCH":
            return {
                "type": "PRODUCT_SEARCH",
                "product": match.group(1).strip(),
                "place": match.group(2).strip(),
                "description": match.group(1).strip(),
                "original_message": original_message,
                "confidence": 0.9
            }
        
        elif intent_type == "MEDIA_GENERATION":
            full_prompt = match.group(1).strip()
            media_type = self._detect_media_type(full_prompt)
            
            return {
                "type": "MEDIA_GENERATION",
                "media_type": media_type,
                "prompt": full_prompt,
                "original_message": original_message,
                "confidence": 0.85
            }
        
        elif intent_type == "REMINDER":
            action = match.group(1).strip()
            time_str = match.group(2).strip()
            
            return {
                "type": "REMINDER",
                "action": action,
                "time_string": time_str,
                "recurring": self._is_recurring(time_str),
                "original_message": original_message,
                "confidence": 0.9
            }
        
        elif intent_type == "MEMORY_STORE":
            return {
                "type": "MEMORY_STORE",
                "information": match.group(1).strip(),
                "original_message": original_message,
                "confidence": 0.95
            }
        
        return {"type": "UNKNOWN", "confidence": 0.0}
    
    def _detect_media_type(self, prompt: str) -> str:
        """Detect media type from prompt"""
        prompt_lower = prompt.lower()
        
        for media_type, keywords in self.MEDIA_TYPES.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return media_type
        
        return "image"
    
    def _is_recurring(self, time_str: str) -> bool:
        """Detect if time expression indicates recurring event"""
        recurring_keywords = [
            "every", "daily", "weekly", "monthly", "yearly",
            "each", "hourly", "regularly"
        ]
        return any(keyword in time_str.lower() for keyword in recurring_keywords)