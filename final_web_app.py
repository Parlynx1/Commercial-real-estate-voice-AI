from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import logging
import os
import base64
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Commercial Real Estate Voice AI - Web App",
    description="Full-Featured Commercial Real Estate AI with Web Interface",
    version="1.0.0"
)

# Enhanced CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize OpenAI client with better error handling
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = None

if OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-'):
    try:
        import openai
        # Try different initialization methods for compatibility
        try:
            openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
            # Test with a simple call
            models = openai_client.models.list()
            logger.info("✅ OpenAI client initialized successfully")
        except Exception as init_error:
            logger.warning(f"⚠️ OpenAI client initialization failed: {init_error}")
            # Try alternative initialization
            try:
                openai.api_key = OPENAI_API_KEY
                logger.info("✅ OpenAI initialized with legacy method")
            except:
                openai_client = None
                logger.warning("⚠️ All OpenAI initialization methods failed")
    except ImportError:
        logger.warning("⚠️ OpenAI library not installed")
        openai_client = None
else:
    logger.info("⚠️ No valid OpenAI API key found - using mock responses")

# Load property data
import pandas as pd

def load_properties():
    try:
        df = pd.read_csv('data/properties.csv')
        logger.info(f"📊 Loaded {len(df)} properties from CSV")
        return df
    except Exception as e:
        logger.warning(f"Could not load properties CSV: {e}")
        # Sample data for demo
        return pd.DataFrame({
            'unique_id': ['PROP001', 'PROP002', 'PROP003', 'PROP004', 'PROP005'],
            'Property Address': [
                '123 Innovation Drive Downtown',
                '456 Tech Plaza Midtown', 
                '789 Business Center Uptown',
                '321 Creative Commons Arts District',
                '654 Executive Tower Financial District'
            ],
            'Floor': [5, 8, 3, 2, 15],
            'Suite': ['A', 'B', 'C', 'E', 'F'],
            'Size (SF)': [2500, 3200, 1800, 2000, 5000],
            'Rent/SF/Year': [28.00, 32.00, 25.00, 26.00, 42.00],
            'Associate 1': ['John Smith', 'Lisa Brown', 'David Miller', 'Michael Clark', 'Susan Young'],
            'BROKER Email ID': ['john@broker.com', 'lisa@broker.com', 'david@broker.com', 'michael@broker.com', 'susan@broker.com'],
            'Annual Rent': [70000, 102400, 45000, 52000, 210000],
            'Monthly Rent': [5833.33, 8533.33, 3750.00, 4333.33, 17500.00]
        })

properties_df = load_properties()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = []
    rag_context: Optional[str] = None
    emotion_data: Optional[Dict[str, Any]] = None

class SpeechRequest(BaseModel):
    text: str
    provider: Optional[str] = None
    voice_id: Optional[str] = None
    emotion_context: Optional[Dict[str, Any]] = None

# Service functions
def analyze_emotion_from_text(text: str) -> Dict[str, Any]:
    """Simple but effective emotion analysis"""
    text_lower = text.lower()
    
    enthusiasm_keywords = ["excited", "love", "amazing", "perfect", "great", "fantastic", "wow", "awesome"]
    professional_keywords = ["need", "require", "business", "professional", "office", "company", "corporate"]
    uncertainty_keywords = ["maybe", "perhaps", "not sure", "uncertain", "think", "might", "possibly"]
    confidence_keywords = ["definitely", "certainly", "absolutely", "sure", "confident", "know", "clear"]
    
    word_count = max(len(text_lower.split()), 1)
    
    enthusiasm_level = min(sum(1 for word in enthusiasm_keywords if word in text_lower) / word_count * 8, 1.0)
    professional_level = min(sum(1 for word in professional_keywords if word in text_lower) / word_count * 5, 1.0)
    uncertainty_level = min(sum(1 for word in uncertainty_keywords if word in text_lower) / word_count * 8, 1.0)
    confidence_level = min(sum(1 for word in confidence_keywords if word in text_lower) / word_count * 8, 1.0)
    
    emotion_score = 0.5 + (enthusiasm_level + confidence_level - uncertainty_level) * 0.3
    emotion_score = max(0.0, min(1.0, emotion_score))
    
    return {
        "emotion_score": emotion_score,
        "enthusiasm_level": enthusiasm_level,
        "voice_pace": 1.0 + (enthusiasm_level - 0.5) * 0.4,
        "tone_analysis": {
            "professional": professional_level,
            "excited": enthusiasm_level,
            "confident": confidence_level,
            "uncertain": uncertainty_level
        }
    }

def find_matching_properties(message: str) -> List[Dict[str, Any]]:
    """Smart property matching based on message content"""
    import re
    
    text_lower = message.lower()
    matches = []
    
    # Extract number of people and convert to square footage
    people_patterns = [
        r'(\d+)\s*people',
        r'team\s*of\s*(\d+)',
        r'(\d+)\s*employees',
        r'(\d+)\s*person\s*team'
    ]
    
    for pattern in people_patterns:
        match = re.search(pattern, text_lower)
        if match:
            people_count = int(match.group(1))
            min_size = people_count * 100  # 100 sq ft per person
            max_size = people_count * 200  # 200 sq ft per person
            
            size_matches = properties_df[
                (properties_df['Size (SF)'] >= min_size) & 
                (properties_df['Size (SF)'] <= max_size)
            ]
            if not size_matches.empty:
                matches.extend(size_matches.to_dict('records'))
            break
    
    # Extract budget constraints
    budget_patterns = [
        r'\$(\d+)\s*(?:per\s*)?(?:sq\.?\s*ft\.?|square\s*foot)',
        r'budget.*?\$(\d+)',
        r'around\s*\$(\d+)',
        r'under\s*\$(\d+)'
    ]
    
    for pattern in budget_patterns:
        match = re.search(pattern, text_lower)
        if match:
            budget = float(match.group(1))
            budget_matches = properties_df[properties_df['Rent/SF/Year'] <= budget * 1.2]
            if not budget_matches.empty:
                matches.extend(budget_matches.to_dict('records'))
            break
    
    # Location matching
    location_keywords = {
        'downtown': 'Downtown',
        'midtown': 'Midtown', 
        'uptown': 'Uptown',
        'financial': 'Financial',
        'tech': 'Tech',
        'creative': 'Creative',
        'arts': 'Arts'
    }
    
    for keyword, location in location_keywords.items():
        if keyword in text_lower:
            location_matches = properties_df[
                properties_df['Property Address'].str.contains(location, case=False, na=False)
            ]
            if not location_matches.empty:
                matches.extend(location_matches.to_dict('records'))
    
    # Remove duplicates and return top 3
    if matches:
        unique_matches = []
        seen_ids = set()
        for match in matches:
            if match['unique_id'] not in seen_ids:
                unique_matches.append(match)
                seen_ids.add(match['unique_id'])
        return unique_matches[:3]
    
    # If no specific matches, return top 3 general properties
    return properties_df.head(3).to_dict('records')

def generate_response_with_properties(message: str, properties: List[Dict[str, Any]], emotion_data: Optional[Dict] = None) -> str:
    """Generate intelligent response with property recommendations"""
    
    if not properties:
        return """I'd love to help you find the perfect office space! To give you the best recommendations, could you tell me:

• How many people will work in the space?
• What's your budget per square foot?
• Any preferred location (downtown, midtown, etc.)?
• What type of business are you in?

The more details you provide, the better I can match you with ideal properties!"""
    
    # Build response based on emotion
    response_parts = []
    
    if emotion_data and emotion_data.get('enthusiasm_level', 0) > 0.6:
        response_parts.append("I'm excited to help you! I found some perfect properties that match your needs:")
    elif emotion_data and emotion_data.get('tone_analysis', {}).get('professional', 0) > 0.7:
        response_parts.append("Excellent. I've identified several professional properties that meet your requirements:")
    else:
        response_parts.append("Great! I found some excellent properties that would be perfect for you:")
    
    response_parts.append("")
    
    # Add property details
    for i, prop in enumerate(properties, 1):
        response_parts.append(f"🏢 **{prop['Property Address']}**")
        response_parts.append(f"   • {prop['Size (SF)']:,} square feet on Floor {prop['Floor']}, Suite {prop['Suite']}")
        response_parts.append(f"   • ${prop['Rent/SF/Year']}/sq ft/year (${prop['Monthly Rent']:,.2f}/month)")
        response_parts.append(f"   • Annual rent: ${prop['Annual Rent']:,.2f}")
        response_parts.append(f"   • Contact: {prop['Associate 1']} ({prop['BROKER Email ID']})")
        response_parts.append("")
    
    # Add follow-up based on emotion
    if emotion_data and emotion_data.get('enthusiasm_level', 0) > 0.7:
        response_parts.append("These spaces would be fantastic for your team! Would you like me to arrange virtual tours right away?")
    else:
        response_parts.append("Would you like more details about any of these properties or help scheduling a tour?")
    
    return "\n".join(response_parts)

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve a working web interface"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>Commercial Real Estate Voice AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }
        .container { 
            max-width: 1200px; margin: 0 auto; background: white; 
            border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50, #34495e); color: white; 
            padding: 30px; text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .status { margin-top: 15px; font-size: 0.9em; }
        .status-dot { 
            display: inline-block; width: 12px; height: 12px; border-radius: 50%; 
            margin-right: 8px; animation: pulse 2s infinite;
        }
        .connected { background: #28a745; }
        .disconnected { background: #dc3545; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        .main-content { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; padding: 30px; }
        .section { background: #f8f9fa; border-radius: 15px; padding: 25px; }
        .section-title { font-size: 1.5em; color: #2c3e50; margin-bottom: 20px; }
        
        .chat-container { 
            background: white; border-radius: 10px; height: 400px; overflow-y: auto;
            padding: 15px; margin-bottom: 15px; border: 2px solid #e9ecef;
        }
        .message { 
            margin-bottom: 15px; padding: 12px 16px; border-radius: 12px; 
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .user-message { 
            background: linear-gradient(135deg, #007bff, #0056b3); color: white; 
            margin-left: 20%; border-bottom-right-radius: 4px;
        }
        .ai-message { 
            background: #e9ecef; color: #2c3e50; margin-right: 20%; 
            border-bottom-left-radius: 4px;
        }
        .message-time { font-size: 0.8em; opacity: 0.7; margin-top: 5px; }
        
        .input-section { display: flex; gap: 10px; align-items: center; }
        .text-input { 
            flex: 1; padding: 12px; border: 2px solid #e9ecef; border-radius: 25px; 
            font-size: 1em; outline: none;
        }
        .text-input:focus { border-color: #007bff; }
        
        .voice-controls { text-align: center; margin-bottom: 30px; }
        .record-button { 
            width: 120px; height: 120px; border-radius: 50%; border: none; 
            font-size: 2.5em; cursor: pointer; transition: all 0.3s ease; margin-bottom: 20px;
        }
        .record-idle { 
            background: linear-gradient(135deg, #28a745, #20c997); color: white;
            box-shadow: 0 8px 25px rgba(40, 167, 69, 0.3);
        }
        .record-active { 
            background: linear-gradient(135deg, #dc3545, #c82333); color: white;
            animation: recordPulse 1s infinite; box-shadow: 0 8px 25px rgba(220, 53, 69, 0.5);
        }
        @keyframes recordPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }
        
        .send-button { 
            padding: 12px 24px; background: linear-gradient(135deg, #007bff, #0056b3); 
            color: white; border: none; border-radius: 25px; cursor: pointer; 
            font-size: 1em; transition: all 0.3s;
        }
        .send-button:hover { transform: translateY(-2px); }
        
        .emotion-display { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .emotion-bar { margin-bottom: 12px; }
        .emotion-label { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.9em; }
        .emotion-progress { background: #e9ecef; border-radius: 10px; height: 8px; overflow: hidden; }
        .emotion-fill { height: 100%; border-radius: 10px; transition: width 0.5s ease; }
        .enthusiasm-fill { background: linear-gradient(90deg, #28a745, #20c997); }
        .professional-fill { background: linear-gradient(90deg, #007bff, #0056b3); }
        .confidence-fill { background: linear-gradient(90deg, #6f42c1, #5a32a3); }
        .uncertainty-fill { background: linear-gradient(90deg, #ffc107, #e0a800); }
        
        .properties-section { 
            grid-column: 1 / -1; background: #f8f9fa; border-radius: 15px; 
            padding: 25px; margin-top: 20px;
        }
        .property-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 20px; margin-top: 20px;
        }
        .property-card { 
            background: white; border-radius: 15px; padding: 20px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.3s ease;
        }
        .property-card:hover { transform: translateY(-5px); }
        .property-header { font-size: 1.2em; font-weight: bold; color: #2c3e50; margin-bottom: 15px; }
        .property-details { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px; }
        .detail-item { color: #6c757d; font-size: 0.9em; }
        .detail-value { font-weight: bold; color: #2c3e50; }
        
        @media (max-width: 768px) { 
            .main-content { grid-template-columns: 1fr; }
            .property-details { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏢 Commercial Real Estate Voice AI</h1>
            <p>Find Your Perfect Office Space with AI-Powered Voice Assistance</p>
            <div class="status">
                <span id="status-dot" class="status-dot disconnected"></span>
                <span id="status-text">Connecting to AI...</span>
            </div>
        </div>
        
        <div class="main-content">
            <div class="section">
                <div class="section-title">💬 AI Chat Assistant</div>
                <div class="chat-container" id="chat-container">
                    <div class="message ai-message">
                        <div>Hello! I'm your Commercial Real Estate AI assistant. I can help you find the perfect office space for your business.</div>
                        <div class="message-time">Just now</div>
                    </div>
                </div>
                <div class="input-section">
                    <input type="text" class="text-input" id="message-input" placeholder="Type your message..." onkeypress="handleEnter(event)">
                    <button class="send-button" onclick="sendMessage()">Send</button>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">🎤 Voice Assistant</div>
                <div class="voice-controls">
                    <button class="record-button record-idle" id="record-button" onclick="toggleRecording()">🎤</button>
                    <div id="record-status">Click to start voice recording</div>
                </div>
                
                <div class="emotion-display">
                    <div style="font-weight: bold; margin-bottom: 15px; color: #2c3e50;">🎭 Voice Emotion Analysis</div>
                    <div class="emotion-bar">
                        <div class="emotion-label"><span>Enthusiasm</span><span id="enthusiasm-value">50%</span></div>
                        <div class="emotion-progress"><div class="emotion-fill enthusiasm-fill" id="enthusiasm-bar" style="width: 50%"></div></div>
                    </div>
                    <div class="emotion-bar">
                        <div class="emotion-label"><span>Professional</span><span id="professional-value">50%</span></div>
                        <div class="emotion-progress"><div class="emotion-fill professional-fill" id="professional-bar" style="width: 50%"></div></div>
                    </div>
                    <div class="emotion-bar">
                        <div class="emotion-label"><span>Confidence</span><span id="confidence-value">50%</span></div>
                        <div class="emotion-progress"><div class="emotion-fill confidence-fill" id="confidence-bar" style="width: 50%"></div></div>
                    </div>
                    <div class="emotion-bar">
                        <div class="emotion-label"><span>Uncertainty</span><span id="uncertainty-value">30%</span></div>
                        <div class="emotion-progress"><div class="emotion-fill uncertainty-fill" id="uncertainty-bar" style="width: 30%"></div></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="properties-section">
            <div class="section-title">🏠 Recommended Properties</div>
            <div id="properties-status">Start a conversation to see property recommendations...</div>
            <div class="property-grid" id="property-grid"></div>
        </div>
    </div>

    <script>
        let isRecording = false;
        let mediaRecorder = null;
        let audioChunks = [];

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            checkConnection();
            addSampleMessage();
        });

        async function checkConnection() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                document.getElementById('status-dot').className = 'status-dot connected';
                document.getElementById('status-text').textContent = `Connected - ${data.properties_count} properties loaded`;
            } catch (error) {
                document.getElementById('status-dot').className = 'status-dot disconnected';
                document.getElementById('status-text').textContent = 'Connection failed - Check server';
            }
        }

        function addSampleMessage() {
            setTimeout(() => {
                addMessage('ai', 'Try saying: "I need office space for 25 people downtown" or "Looking for modern workspace under $30 per square foot"');
            }, 2000);
        }

        function handleEnter(event) {
            if (event.key === 'Enter') sendMessage();
        }

        async function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            if (!message) return;

            addMessage('user', message);
            input.value = '';

            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: message,
                        conversation_history: [],
                        emotion_data: null
                    })
                });
                
                const data = await response.json();
                addMessage('ai', data.response);
                extractProperties(data.response);
            } catch (error) {
                addMessage('ai', 'Sorry, I encountered an error. Please try again.');
            }
        }

        async function toggleRecording() {
            if (!isRecording) {
                startRecording();
            } else {
                stopRecording();
            }
        }

        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
                mediaRecorder.onstop = processRecording;
                
                mediaRecorder.start();
                isRecording = true;
                
                document.getElementById('record-button').className = 'record-button record-active';
                document.getElementById('record-button').textContent = '⏹️';
                document.getElementById('record-status').textContent = 'Recording... Click to stop';
            } catch (error) {
                document.getElementById('record-status').textContent = 'Microphone access denied';
            }
        }

        function stopRecording() {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            
            document.getElementById('record-button').className = 'record-button record-idle';
            document.getElementById('record-button').textContent = '⏳';
            document.getElementById('record-status').textContent = 'Processing...';
        }

        async function processRecording() {
            try {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.wav');
                formData.append('session_id', 'web_session');
                formData.append('include_audio_response', 'true');
                
                const response = await fetch('/api/v1/converse', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                addMessage('user', data.transcript + ' 🎤');
                addMessage('ai', data.response);
                updateEmotions(data.emotion_analysis);
                extractProperties(data.response);
                
                document.getElementById('record-status').textContent = `Processed in ${data.processing_times.total_time.toFixed(2)}s`;
            } catch (error) {
                document.getElementById('record-status').textContent = 'Error processing voice';
            } finally {
                document.getElementById('record-button').className = 'record-button record-idle';
                document.getElementById('record-button').textContent = '🎤';
                setTimeout(() => {
                    document.getElementById('record-status').textContent = 'Click to start voice recording';
                }, 3000);
            }
        }

        function addMessage(sender, text) {
            const container = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            messageDiv.innerHTML = `<div>${text}</div><div class="message-time">${time}</div>`;
            
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }

        function updateEmotions(emotions) {
            const enthusiasm = Math.round(emotions.enthusiasm_level * 100);
            const professional = Math.round(emotions.tone_analysis.professional * 100);
            const confidence = Math.round(emotions.tone_analysis.confident * 100);
            const uncertainty = Math.round(emotions.tone_analysis.uncertain * 100);
            
            document.getElementById('enthusiasm-value').textContent = enthusiasm + '%';
            document.getElementById('enthusiasm-bar').style.width = enthusiasm + '%';
            
            document.getElementById('professional-value').textContent = professional + '%';
            document.getElementById('professional-bar').style.width = professional + '%';
            
            document.getElementById('confidence-value').textContent = confidence + '%';
            document.getElementById('confidence-bar').style.width = confidence + '%';
            
            document.getElementById('uncertainty-value').textContent = uncertainty + '%';
            document.getElementById('uncertainty-bar').style.width = uncertainty + '%';
        }

        function extractProperties(response) {
            const propertyPattern = /🏢\s*\*\*(.*?)\*\*/g;
            const matches = [...response.matchAll(propertyPattern)];
            
            if (matches.length > 0) {
                document.getElementById('properties-status').textContent = `Found ${matches.length} property recommendation(s):`;
                const grid = document.getElementById('property-grid');
                grid.innerHTML = '';
                
                matches.forEach((match, index) => {
                    const propertyName = match[1];
                    createPropertyCard(propertyName, response, index);
                });
            }
        }

        function createPropertyCard(name, response, index) {
            const grid = document.getElementById('property-grid');
            const card = document.createElement('div');
            card.className = 'property-card';
            
            // Extract details from response
            const lines = response.split('\\n');
            let size = 'Contact for details';
            let rent = 'Contact for pricing';
            let contact = 'See response above';
            
            for (const line of lines) {
                if (line.includes(name)) {
                    const nextLines = lines.slice(lines.indexOf(line), lines.indexOf(line) + 5);
                    for (const nextLine of nextLines) {
                        if (nextLine.includes('sq ft')) {
                            const sizeMatch = nextLine.match(/(\d{1,3}(?:,\d{3})*)\s*sq/);
                            if (sizeMatch) size = sizeMatch[1] + ' sq ft';
                        }
                        if (nextLine.includes('/sq ft/year')) {
                            const rentMatch = nextLine.match(/\$(\d+(?:\.\d{2})?)/);
                            if (rentMatch) rent = ' + rentMatch[1] + '/sq ft/year';
                        }
                        if (nextLine.includes('Contact:')) {
                            contact = nextLine.replace('Contact:', '').trim();
                        }
                    }
                    break;
                }
            }
            
            card.innerHTML = `
                <div class="property-header">🏢 ${name}</div>
                <div class="property-details">
                    <div class="detail-item">
                        <strong>Size:</strong>
                        <div class="detail-value">${size}</div>
                    </div>
                    <div class="detail-item">
                        <strong>Rent:</strong>
                        <div class="detail-value">${rent}</div>
                    </div>
                    <div class="detail-item">
                        <strong>Contact:</strong>
                        <div class="detail-value">${contact}</div>
                    </div>
                    <div class="detail-item">
                        <strong>Status:</strong>
                        <div class="detail-value">Available Now</div>
                    </div>
                </div>
            `;
            
            grid.appendChild(card);
        }
    </script>
</body>
</html>
    """)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "openai_available": openai_client is not None,
        "properties_count": len(properties_df),
        "web_interface": "available"
    }

@app.post("/api/v1/chat")
async def chat_with_llm(request: ChatRequest):
    try:
        start_time = time.time()
        
        # Find matching properties
        properties = find_matching_properties(request.message)
        
        # Analyze emotion
        emotion_data = request.emotion_data or analyze_emotion_from_text(request.message)
        
        # Generate response
        response = generate_response_with_properties(request.message, properties, emotion_data)
        
        return {
            "response": response,
            "processing_time": time.time() - start_time,
            "tokens_used": 150,
            "model": "smart-property-matcher",
            "rag_sources_used": False
        }
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    provider: str = Form("auto")
):
    try:
        start_time = time.time()
        audio_data = await audio_file.read()
        
        # Smart mock transcription based on audio size
        mock_transcripts = [
            "I need office space for my 25 person tech startup. We're looking for something modern and collaborative downtown.",
            "We need professional office space for our law firm. Private offices and conference rooms are essential. Budget around $40 per square foot.",
            "Looking for creative workspace for 15 people in the arts district. We want something inspiring and unique.",
            "Need large corporate space for 50 employees in the financial district. Professional environment is very important."
        ]
        
        transcript = mock_transcripts[len(audio_data) % len(mock_transcripts)]
        emotion_data = analyze_emotion_from_text(transcript)
        
        return {
            "transcript": transcript,
            "confidence": 0.95,
            "transcription_time": time.time() - start_time,
            "provider": "smart_mock",
            "emotion_analysis": emotion_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/speak")
async def text_to_speech(request: SpeechRequest):
    try:
        start_time = time.time()
        mock_audio = base64.b64encode(b"mock_audio_" + request.text[:20].encode()).decode()
        
        return {
            "audio_data": mock_audio,
            "generation_time": time.time() - start_time,
            "provider": "mock",
            "voice_id": "mock-voice",
            "text_length": len(request.text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/converse")
async def full_conversation_pipeline(
    audio_file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    include_audio_response: bool = Form(True)
):
    try:
        audio_data = await audio_file.read()
        
        # Get transcription
        transcription_result = await transcribe_audio(audio_file)
        transcript = transcription_result["transcript"]
        emotion_analysis = transcription_result["emotion_analysis"]
        
        # Generate chat response
        chat_request = ChatRequest(message=transcript, emotion_data=emotion_analysis)
        chat_result = await chat_with_llm(chat_request)
        
        # Generate TTS if requested
        audio_response = None
        tts_time = 0
        if include_audio_response:
            tts_request = SpeechRequest(text=chat_result["response"])
            tts_result = await text_to_speech(tts_request)
            audio_response = tts_result["audio_data"]
            tts_time = tts_result["generation_time"]
        
        return {
            "transcript": transcript,
            "response": chat_result["response"],
            "audio_response": audio_response,
            "emotion_analysis": emotion_analysis,
            "processing_times": {
                "transcription_time": transcription_result["transcription_time"],
                "llm_processing_time": chat_result["processing_time"],
                "tts_generation_time": tts_time,
                "total_time": transcription_result["transcription_time"] + chat_result["processing_time"] + tts_time
            },
            "session_id": session_id or "default_session"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🌐 Starting Commercial Real Estate Voice AI Web Application")
    print("=" * 60)
    print("🚀 Web Interface: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🎤 Features: Voice Recording, Chat, Property Matching")
    print("=" * 60)
    
    import uvicorn
    uvicorn.run(
        "final_web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )