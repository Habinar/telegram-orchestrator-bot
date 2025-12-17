from typing import Dict

class AgentRouter:
    """Select optimal agent based on intent"""
    
    AGENT_MAP = {
        "PRODUCT_SEARCH": {
            "primary": "perplexity",
            "fallbacks": ["exa", "google-search"],
            "cost": "medium"
        },
        "MEDIA_GENERATION": {
            "image": {
                "primary": "gemini-nano-banana-pro",
                "fallbacks": ["flux-redux-image-restyler", "ideogramv2-imagegen"],
                "cost": "high"
            },
            "video": {
                "primary": "deepmind-veo3-video",
                "fallbacks": [],
                "cost": "very_high"
            },
            "audio": {
                "primary": "soundeffectsgenerator",
                "fallbacks": [],
                "cost": "medium"
            },
            "voice": {
                "primary": "tts-playAI-v3",
                "fallbacks": ["tts-minimax-turbo"],
                "cost": "low"
            }
        },
        "REMINDER": {
            "primary": "bhindi-scheduler-v2",
            "fallbacks": [],
            "cost": "free"
        },
        "MEMORY_STORE": {
            "primary": "bhindi-notes-v2",
            "fallbacks": [],
            "cost": "free"
        }
    }
    
    def select_agent(self, intent: Dict, attempt: int = 1) -> str:
        """Select best agent for intent"""
        intent_type = intent["type"]
        
        if intent_type not in self.AGENT_MAP:
            return "perplexity"
        
        config = self.AGENT_MAP[intent_type]
        
        if intent_type == "MEDIA_GENERATION":
            media_type = intent.get("media_type", "image")
            config = config.get(media_type, config["image"])
        
        if attempt == 1:
            return config["primary"]
        
        fallbacks = config.get("fallbacks", [])
        if attempt - 2 < len(fallbacks):
            return fallbacks[attempt - 2]
        
        return config["primary"]
    
    def get_agent_info(self, agent_id: str, intent: Dict) -> Dict:
        """Get agent metadata for transparency"""
        reasons = {
            "gemini-nano-banana-pro": "Best quality for image generation",
            "perplexity": "Most reliable for web search",
            "bhindi-scheduler-v2": "Native scheduling with Telegram integration",
            "bhindi-notes-v2": "Persistent memory storage"
        }
        
        return {
            "agent_id": agent_id,
            "reason": reasons.get(agent_id, f"Optimal for {intent['type']}"),
            "expected_time": "10-30 seconds"
        }