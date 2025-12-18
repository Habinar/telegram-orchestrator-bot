from typing import Dict
from parsers.intent_parser import IntentParser
from agents.router import AgentRouter
from agents.validator import RigorousValidator
from agents.openai_executor import OpenAIExecutor
import config

class Orchestrator:
    """Core orchestration engine with OpenAI"""
    
    def __init__(self):
        self.parser = IntentParser()
        self.router = AgentRouter()
        self.validator = RigorousValidator()
        self.executor = OpenAIExecutor()
        self.max_retries = config.MAX_RETRIES
    
    async def process(self, message: str, user_id: str, notify_callback) -> Dict:
        """Main orchestration flow"""
        
        # Parse intent
        intent = self.parser.parse(message)
        
        if intent["confidence"] < 0.5:
            # Handle as general query with OpenAI
            intent["type"] = "GENERAL_QUERY"
            intent["message"] = message
        
        # Execute with retries
        for attempt in range(1, self.max_retries + 1):
            agent_id = self.router.select_agent(intent, attempt)
            agent_info = self.router.get_agent_info(agent_id, intent)
            
            # Notify user
            if config.TRANSPARENCY_LEVEL in ["STANDARD", "FULL"]:
                await notify_callback(
                    f"🔍 Using **{agent_id}** (OpenAI-powered)\n"
                    f"📋 {agent_info['reason']}\n"
                    f"⏱ Expected: {agent_info['expected_time']}"
                )
            
            # Execute with OpenAI
            await notify_callback("⚙️ Executing...")
            output = await self.executor.execute(intent)
            
            if not output.get("success", False):
                if attempt < self.max_retries:
                    await notify_callback(f"⚠️ Attempt {attempt} failed: {output.get('error', 'Unknown error')}")
                    await notify_callback("🔄 Retrying...")
                    continue
                else:
                    return {
                        "success": False,
                        "message": "All attempts failed",
                        "error": output.get("error")
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
                    await notify_callback("🔄 Retrying with adjusted parameters...")
        
        return {
            "success": False,
            "message": "Validation failed after all retries",
            "last_output": output,
            "last_validation": validation
        }