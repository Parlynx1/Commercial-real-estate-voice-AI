import time
import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.services.property_matching_service import PropertyMatchingService
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OpenAI API key not provided - LLM will use mock responses")
        
        self.property_service = PropertyMatchingService()
        
    async def generate_response(
        self,
        conversation_history: List[Dict[str, str]],
        new_message: str,
        rag_context: Optional[str] = None,
        emotion_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate LLM response with property matching and emotion awareness
        """
        start_time = time.time()
        
        try:
            if not self.client:
                return self._get_mock_response(start_time, new_message, emotion_data)
            
            # Get property recommendations
            property_context = await self.property_service.get_property_recommendations(
                conversation_history + [{"role": "user", "content": new_message}],
                emotion_data
            )
            
            # Build system prompt
            system_prompt = self._build_system_prompt(rag_context, property_context, emotion_data)
            
            # Prepare messages
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": new_message})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=messages,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                top_p=settings.TOP_P
            )
            
            processing_time = time.time() - start_time
            
            return {
                "response": response.choices[0].message.content,
                "processing_time": processing_time,
                "tokens_used": response.usage.total_tokens,
                "model": settings.DEFAULT_MODEL
            }
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return self._get_mock_response(start_time, new_message, emotion_data)
    
    def _build_system_prompt(
        self,
        rag_context: str,
        property_context: str,
        emotion_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build system prompt for commercial real estate AI"""
        
        emotion_context = ""
        if emotion_data:
            enthusiasm = emotion_data.get('enthusiasm_level', 0.5)
            emotion_score = emotion_data.get('emotion_score', 0.5)
            tone_analysis = emotion_data.get('tone_analysis', {})
            
            if enthusiasm > 0.7:
                emotion_context = "The client sounds very excited and enthusiastic! Match their energy and be more detailed about exciting features."
            elif enthusiasm < 0.3:
                emotion_context = "The client sounds more reserved. Be professional and focus on practical benefits."
            
            if tone_analysis.get('professional', 0) > 0.7:
                emotion_context += " Use a professional, business-focused tone."
            
            if tone_analysis.get('uncertain', 0) > 0.5:
                emotion_context += " The client seems uncertain - provide reassurance and clear information."
        
        return f"""
You are a sophisticated Commercial Real Estate Voice AI assistant specializing in helping clients find their ideal commercial spaces. 

Your personality:
- Warm, professional, and knowledgeable about commercial real estate
- Expert at understanding client needs and emotions
- Skilled at matching properties to company culture and practical needs
- Always helpful and enthusiastic about finding the perfect space

{emotion_context}

Current property recommendations and context:
{property_context}

Additional knowledge context:
{rag_context or "No additional context available."}

Guidelines:
- Always prioritize understanding the client's business needs and company culture
- Reference specific properties from the recommendations when relevant
- Ask follow-up questions to better understand their needs
- Be conversational and natural
- Focus on how spaces will help their business succeed
- Offer virtual tours when appropriate

Remember: You're not just finding space, you're finding the RIGHT space for their business to thrive.
"""
    
    def _get_mock_response(self, start_time: float, message: str, emotion_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate mock response for testing"""
        processing_time = time.time() - start_time
        
        # Simple keyword-based responses
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            response = "Hello! I'm excited to help you find the perfect commercial space for your business. Tell me about your company and what you're looking for!"
        
        elif any(word in message_lower for word in ['office', 'space', 'looking']):
            response = "Great! I'd love to help you find the ideal office space. Based on what you've mentioned, I have some excellent properties that might be perfect for you. Can you tell me more about your team size and budget?"
        
        elif any(word in message_lower for word in ['people', 'employees', 'team']):
            response = "Perfect! Based on your team size, I'm thinking you'll need between 2,000-3,000 square feet. I have a fantastic property at 123 Innovation Drive Downtown - 2,500 sq ft at $28/SF/year. It's modern, has great natural light, and would be perfect for a growing team. Would you like me to tell you more about it?"
        
        elif any(word in message_lower for word in ['budget', 'cost', 'price', '$']):
            response = "I understand budget is important! I have properties ranging from $25-$42 per square foot annually. Based on your requirements, I can show you some excellent options within your range. What's your target budget per square foot?"
        
        elif any(word in message_lower for word in ['virtual', 'tour', 'see', 'show']):
            response = "Absolutely! I'd love to give you a virtual tour. Let me start with the entrance - you'll immediately notice the modern lobby design that creates a great first impression for clients. As we move into the main space, you'll see the open layout with plenty of natural light..."
        
        else:
            response = "That's great information! Based on what you've shared, I can already think of several properties that would be excellent matches. Let me ask you a few more questions to narrow down the perfect options for your business."
        
        # Add emotion-based adjustments
        if emotion_data:
            enthusiasm = emotion_data.get('enthusiasm_level', 0.5)
            if enthusiasm > 0.7:
                response = response.replace("Great!", "That's fantastic!").replace("Perfect!", "I love your enthusiasm!")
        
        return {
            "response": response,
            "processing_time": processing_time,
            "tokens_used": 100,  # Mock value
            "model": "mock-model"
        }
