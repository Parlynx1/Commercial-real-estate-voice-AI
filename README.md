# 🏢 Commercial Real Estate Voice AI

> 🎤 Bidirectional Voice Conversational AI System for Finding the Perfect Commercial Property  
> 🧠 AI with Emotion Analysis • 🤖 Property Matching • 🌐 Full Web Interface

![Commercial Real Estate Voice AI Interface](screenshot.png)

---

## 📌 Overview

**Commercial Real Estate Voice AI** is a full-stack AI-powered web application that allows users to describe their ideal office space via **voice input**. The system intelligently transcribes, analyzes emotion, and matches suitable properties from a database using advanced AI and LLM (Large Language Model) pipelines.

### 🔑 Key Features

- 🎤 **Bidirectional Voice Interaction**: Real-time voice-to-text and text-to-voice communication
- 🧠 **Emotion Analysis**: Detects enthusiasm, professionalism, confidence, and uncertainty
- 🗣️ **Cultural Context Matching**: Adaptive responses based on voice tone and user intent
- 🏢 **Smart Property Matching**: Uses NLP to extract user needs and recommend properties
- 📊 **Data Integration**: Matches from 225+ commercial property listings (CSV-based)
- 🌐 **Modern Web UI**: Clean, responsive frontend with chat and voice assistant interface
- 🧪 **Test Suite Included**: Backend unit testing for API and property matcher

---

## ⚙️ Tech Stack

| Layer       | Technology               |
|-------------|--------------------------|
| Frontend    | HTML, CSS, JavaScript    |
| Backend     | Python, FastAPI          |
| AI Services | OpenAI, Whisper, TTS     |
| Data        | CSV (225+ property records) |
| Emotion     | Voice emotion analysis (custom logic) |
| Deployment  | Localhost or any cloud provider |

---

## 🚀 Quick Start

### 🔧 Installation

1. **Clone the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/commercial-real-estate-voice-ai.git
cd commercial-real-estate-voice-ai
Create and Activate Virtual Environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Create Environment Variables

Rename .env.example to .env and add your keys:

env
Copy
Edit
OPENAI_API_KEY=your_key_here
Run the Application

bash
Copy
Edit
python simple_app.py
Visit http://localhost:8000

 
