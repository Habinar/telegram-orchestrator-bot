from openai import AsyncOpenAI
from typing import Dict, List
import json
import config

class OpenAIExecutor:
    """Execute tasks using OpenAI API"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
    
    async def execute(self, intent: Dict) -> Dict:
        """Execute intent using OpenAI"""
        
        intent_type = intent["type"]
        
        if intent_type == "PRODUCT_SEARCH":
            return await self._search_products(intent)
        elif intent_type == "MEDIA_GENERATION":
            return await self._generate_media(intent)
        elif intent_type == "REMINDER":
            return await self._create_reminder(intent)
        elif intent_type == "MEMORY_STORE":
            return await self._store_memory(intent)
        elif intent_type == "GENERAL_QUERY":
            return await self._handle_general_query(intent)
        
        return {"success": False, "error": "Unknown intent type"}
    
    async def _search_products(self, intent: Dict) -> Dict:
        """Search for products using GPT"""
        
        prompt = f"""Search for "{intent['product']}" on {intent['place']}.
        
Provide exactly 5 results in this JSON format:
{{
    "results": [
        {{
            "name": "Product name",
            "price": "Price with currency",
            "link": "https://example.com/product",
            "description": "Brief description"
        }}
    ]
}}

Make the results realistic and relevant. Include actual product links if possible."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful shopping assistant that provides accurate product search results."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["success"] = True
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_media(self, intent: Dict) -> Dict:
        """Generate media using DALL-E or describe how to generate"""
        
        media_type = intent.get("media_type", "image")
        prompt = intent.get("prompt", "")
        
        if media_type == "image":
            try:
                # Use DALL-E 3 for image generation
                response = await self.client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1
                )
                
                return {
                    "success": True,
                    "url": response.data[0].url,
                    "media_type": "image",
                    "revised_prompt": response.data[0].revised_prompt
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        else:
            # For video/audio, provide guidance
            return {
                "success": True,
                "message": f"To generate {media_type}, I recommend using specialized tools like:\n"
                          f"- Video: Runway, Pika, or Stable Video\n"
                          f"- Audio: ElevenLabs, Mubert, or Suno\n"
                          f"- Voice: ElevenLabs or Play.ht\n\n"
                          f"Your prompt: {prompt}",
                "media_type": media_type
            }
    
    async def _create_reminder(self, intent: Dict) -> Dict:
        """Create reminder using GPT to parse time"""
        
        prompt = f"""Parse this reminder request and create a cron expression:
        
Action: {intent['action']}
Time: {intent['time_string']}
Recurring: {intent.get('recurring', False)}

Provide response in this JSON format:
{{
    "cron_expression": "minute hour day month dayofweek",
    "next_execution": "Human readable time",
    "recurring": true/false,
    "description": "What this reminder does"
}}

Important:
- Use 5-field cron format
- Timezone is Europe/Kiev
- For "every day at 6pm" use: "0 18 * * *"
- For "every Sunday at 6pm" use: "0 18 * * 0"
- For "every 2 hours" use: "0 */2 * * *"
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a scheduling expert that creates accurate cron expressions."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["success"] = True
            result["schedule_id"] = f"reminder-{hash(intent['action'])}"
            result["content"] = f"Reminder: {intent['action']}"
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _store_memory(self, intent: Dict) -> Dict:
        """Store memory (simulated - would use database in production)"""
        
        information = intent.get("information", "")
        
        # In production, this would store to a database
        # For now, we'll just acknowledge storage
        
        return {
            "success": True,
            "note_id": f"note-{hash(information)}",
            "content": information,
            "stored_at": "memory_db",
            "message": "Information stored successfully"
        }
    
    async def _handle_general_query(self, intent: Dict) -> Dict:
        """Handle general queries with GPT"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Provide concise, accurate responses."},
                    {"role": "user", "content": intent.get("message", "")}
                ]
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "type": "general_response"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}