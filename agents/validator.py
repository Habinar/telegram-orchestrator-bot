import validators
import requests
from typing import Dict, List

class RigorousValidator:
    """Rigorous validation with fact-checking"""
    
    def __init__(self):
        self.validation_threshold = 0.85
    
    async def validate(self, output: Dict, intent: Dict, agent_id: str) -> Dict:
        """Run rigorous validation pipeline"""
        
        intent_type = intent["type"]
        
        if intent_type == "PRODUCT_SEARCH":
            return await self._validate_product_search(output, intent)
        elif intent_type == "MEDIA_GENERATION":
            return await self._validate_media_generation(output, intent)
        elif intent_type == "REMINDER":
            return await self._validate_reminder(output, intent)
        elif intent_type == "MEMORY_STORE":
            return await self._validate_memory(output, intent)
        
        return {"score": 1.0, "passed": True, "checks": [], "reason": "No validation needed"}
    
    async def _validate_product_search(self, output: Dict, intent: Dict) -> Dict:
        """Validate product search results"""
        checks = []
        results = output.get("results", [])
        
        check_1 = len(results) >= 5
        checks.append(("completeness", check_1, 0.3))
        
        all_have_links = all("link" in r or "url" in r for r in results)
        checks.append(("has_links", all_have_links, 0.3))
        
        valid_urls = sum(1 for r in results if validators.url(r.get("link", "") or r.get("url", "")))
        url_score = valid_urls / max(len(results), 1)
        checks.append(("url_validity", url_score > 0.8, 0.4))
        
        total_score = sum(weight if passed else 0 for _, passed, weight in checks)
        
        return {
            "score": total_score,
            "passed": total_score >= self.validation_threshold,
            "checks": checks,
            "reason": self._build_reason(checks)
        }
    
    async def _validate_media_generation(self, output: Dict, intent: Dict) -> Dict:
        """Validate media generation"""
        checks = []
        
        file_url = output.get("url") or output.get("file_url")
        file_exists = file_url is not None
        checks.append(("file_exists", file_exists, 0.5))
        
        if file_exists:
            url_valid = validators.url(file_url)
            checks.append(("url_valid", url_valid, 0.5))
        
        total_score = sum(weight if passed else 0 for _, passed, weight in checks)
        
        return {
            "score": total_score,
            "passed": total_score >= self.validation_threshold,
            "checks": checks,
            "reason": self._build_reason(checks)
        }
    
    async def _validate_reminder(self, output: Dict, intent: Dict) -> Dict:
        """Validate reminder creation"""
        checks = []
        
        schedule_id = output.get("schedule_id") or output.get("id")
        checks.append(("created", schedule_id is not None, 0.5))
        
        cron = output.get("cron_expression") or output.get("cronExpression")
        cron_valid = cron and len(cron.split()) == 5
        checks.append(("cron_valid", cron_valid, 0.5))
        
        total_score = sum(weight if passed else 0 for _, passed, weight in checks)
        
        return {
            "score": total_score,
            "passed": total_score >= self.validation_threshold,
            "checks": checks,
            "reason": self._build_reason(checks)
        }
    
    async def _validate_memory(self, output: Dict, intent: Dict) -> Dict:
        """Validate memory storage"""
        checks = []
        
        note_id = output.get("note_id") or output.get("id")
        checks.append(("created", note_id is not None, 1.0))
        
        total_score = sum(weight if passed else 0 for _, passed, weight in checks)
        
        return {
            "score": total_score,
            "passed": total_score >= self.validation_threshold,
            "checks": checks,
            "reason": self._build_reason(checks)
        }
    
    def _build_reason(self, checks: List) -> str:
        """Build human-readable reason"""
        failed = [name for name, passed, _ in checks if not passed]
        if not failed:
            return "All validation checks passed"
        return f"Failed checks: {', '.join(failed)}"