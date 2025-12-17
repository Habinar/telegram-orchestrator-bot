from typing import Dict
from parsers.intent_parser import IntentParser
from agents.router import AgentRouter
from agents.validator import RigorousValidator
import config

class Orchestrator:
    """Core orchestration engine"""
    
    def __init__(self):
        self.parser = IntentParser()
        self.router = AgentRouter()
        self.validator = RigorousValidator()
        self.max_retries = config.MAX_RETRIES
    
    async def process(self, message: str, user_id: str, notify_callback) -> Dict:
        """Main orchestration flow"""
        
        # Parse intent
        intent = self.parser.parse(message)
        
        if intent["confidence"] < 0.5:
            return await self._handle_ambiguity(intent, notify_callback)
        
        # Execute with retries
        for attempt in range(1, self.max_retries + 1):
            agent_id = self.router.select_agent(intent, attempt)
            agent_info = self.router.get_agent_info(agent_id, intent)
            
            # Notify user
            await notify_callback(
                f"🔍 Using **{agent_id}**\n"
                f"📋 {agent_info['reason']}\n"
                f"⏱ Expected: {agent_info['expected_time']}"
            )
            
            # Mock execution for now (will integrate with Bhindi API)
            await notify_callback("⚙️ Executing...")
            output = await self._mock_execute(agent_id, intent)
            
            if not output.get("success", False):
                if attempt < self.max_retries:
                    await notify_callback(f"⚠️ Attempt {attempt} failed, retrying...")
                    continue
                else:
                    return {
                        "success": False,
                        "message": "All attempts failed"
                    }
            
            # Validate
            await notify_callback("🔬 Running rigorous validation...")
            validation = await self.validator.validate(output, intent, agent_id)
            
            if validation["passed"]:
                await notify_callback(f"✅ Validation passed (score: {validation['score']:.2f})")
                return {
                    "success": True,
                    "output": output,
                    "validation": validation,
                    "agent": agent_id
                }
            else:
                await notify_callback(
                    f"⚠️ Validation failed: {validation['reason']}\n"
                    f"Score: {validation['score']:.2f} (required: 0.85)"
                )
                
                if attempt < self.max_retries:
                    await notify_callback("🔄 Retrying with fallback agent...")
        
        return {
            "success": False,
            "message": "Validation failed after all retries"
        }
    
    async def _handle_ambiguity(self, intent: Dict, notify_callback) -> Dict:
        """Handle ambiguous requests"""
        await notify_callback(
            "❓ I need clarification. Could you please:\n"
            "• Be more specific\n"
            "• Provide more details\n"
            "• Rephrase your request"
        )
        return {
            "success": False,
            "needs_clarification": True
        }
    
    async def _mock_execute(self, agent_id: str, intent: Dict) -> Dict:
        """Mock execution - will be replaced with real Bhindi API calls"""
        # This is a placeholder that returns mock data
        # Once we have the Bhindi API key, this will make real API calls
        
        if intent["type"] == "PRODUCT_SEARCH":
            return {
                "success": True,
                "results": [
                    {"name": f"Product {i}", "link": f"https://example.com/{i}", "price": "$99"}
                    for i in range(1, 6)
                ]
            }
        elif intent["type"] == "MEDIA_GENERATION":
            return {
                "success": True,
                "url": "https://example.com/generated-image.jpg",
                "media_type": intent.get("media_type", "image")
            }
        elif intent["type"] == "REMINDER":
            return {
                "success": True,
                "schedule_id": "mock-123",
                "cronExpression": "0 18 * * *",
                "recurring": intent.get("recurring", False)
            }
        elif intent["type"] == "MEMORY_STORE":
            return {
                "success": True,
                "note_id": "mock-note-123",
                "content": intent.get("information", "")
            }
        
        return {"success": False, "error": "Unknown intent type"}