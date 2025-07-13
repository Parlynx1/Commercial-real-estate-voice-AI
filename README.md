# 🏢 Commercial Real Estate Voice AI

🎤 Bidirectional Voice Conversational AI System for Finding the Perfect Commercial Property  
🧠 AI with Emotion Analysis • 🤖 Property Matching • 🌐 Full Web Interface

![Commercial Real Estate Voice AI Interface](Voice%20AI%20interface.png)

---

## 📌 Overview

**Commercial Real Estate Voice AI** is a full-stack AI-powered web application that allows users to describe their ideal office space via **voice input**. The system intelligently transcribes, analyzes emotion, and matches suitable properties from a database using advanced AI and LLM (Large Language Model) pipelines.

---

## 🔑 Key Features

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

git clone https://github.com/YOUR_USERNAME/commercial-real-estate-voice-ai.git
cd commercial-real-estate-voice-ai
Create and Activate Virtual Environment

2. **Create and Activate Virtual Environment**
   
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
Install Dependencies

3. **Install Dependencies**
   
pip install -r requirements.txt

4. **Create Environment Variables**
   
Create Environment Variables
Rename .env.example to .env and add your keys:

env
OPENAI_API_KEY=your_key_here
Run the Application

5. **Run the Application**
   
python final_web_app.py
Visit http://localhost:8000

## 🔍 API Endpoints

| Endpoint           | Method | Description                          |
|--------------------|--------|--------------------------------------|
| `/chat/`           | POST   | Handles chat messages (voice/text)   |
| `/transcribe/`     | POST   | Transcribes audio to text            |
| `/tts/`            | POST   | Converts text to audio (TTS)         |
| `/match-property/` | POST   | Returns best property match          |
| `/analyze-emotion/`| POST   | Detects vocal emotions from audio    |


## 🧱 Project Structure

```text
commercial-real-estate-voice-ai/
├── app/
│   ├── api/
│   ├── services/
│   ├── utils/
├── data/
│   └── property_listings.csv
├── tests/
├── simple_app.py
├── working_app_fixed.py
├── test_api.py
├── requirements.txt
├── README.md
├── .env.example
└── Voice AI interface.png
```
🧪 Testing
To run unit tests:

pytest test_api.py
🛠️ Deployment Options
✅ Localhost (default FastAPI server)

☁️ Deploy to Render, Vercel (frontend only), Heroku, or AWS EC2

❗ Troubleshooting
Issue	Fix
API Key not found	Ensure .env file is present and properly configured
Microphone not working	Check browser microphone permissions
Emotion analysis not accurate	Ensure high-quality voice recording (clear speech, minimal noise)

🤝 Contributing
## 👥 Contributors

- [@Parlynx1](https://github.com/Parlynx1) - Creator  
- [@varshitmanepalli](https://github.com/varshitmanepalli) - Contributor  


# Fork the repo and clone it
git checkout -b feature/YourFeature
git commit -m "Add awesome feature"
git push origin feature/YourFeature
Then create a Pull Request 🎉

📄 License
MIT License © 2025 Pardhu Mattupalli

📫 Contact
For questions, suggestions, or collaboration:

📧 Email: pmattupa@mail.yu.edu

🌐 LinkedIn: Pardhu Mattupalli

🧠 Acknowledgments
Okada & Company for inspiration

OpenAI for APIs

FastAPI for seamless API development

🌟 Showcase-Ready Highlights
✅ Real AI capabilities

✅ Fully working prototype

✅ Clean, responsive UI

✅ Strong backend architecture

✅ AI pipeline from voice → emotion → response → property match
