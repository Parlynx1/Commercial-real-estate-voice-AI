import requests
import json
import time
import os

# Test the API endpoints
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print("✅ Health Check:", response.json())
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_basic_endpoints():
    """Test basic endpoints"""
    print("\n=== Testing Basic Endpoints ===")
    
    try:
        # Test root endpoint
        response = requests.get(BASE_URL)
        print("✅ Root:", response.json()["message"])
        
        # Test health endpoint
        return test_health()
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running:")
        print("   python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Basic endpoints test failed: {e}")
        return False

def test_chat_endpoint():
    """Test chat endpoint with sample data"""
    print("\n=== Testing Chat Endpoint ===")
    
    try:
        chat_data = {
            "message": "Hi, I need office space for my 20-person tech startup. We're looking for something modern and collaborative around $30 per square foot.",
            "conversation_history": [],
            "emotion_data": {
                "enthusiasm_level": 0.8,
                "emotion_score": 0.7,
                "tone_analysis": {
                    "excited": 0.7,
                    "professional": 0.6,
                    "confident": 0.8
                }
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat Response Generated:")
            print(f"   Response: {result['response'][:100]}...")
            print(f"   Processing Time: {result['processing_time']:.2f}s")
            print(f"   Model: {result['model']}")
            return True
        else:
            print(f"❌ Chat Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def test_tts_endpoint():
    """Test text-to-speech endpoint"""
    print("\n=== Testing Text-to-Speech Endpoint ===")
    
    try:
        tts_data = {
            "text": "I found some excellent properties for your tech startup! Let me tell you about this amazing space in the Innovation District.",
            "emotion_context": {
                "enthusiasm_level": 0.8,
                "emotion_score": 0.7
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/speak", json=tts_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ TTS Response Generated:")
            print(f"   Generation Time: {result['generation_time']:.2f}s")
            print(f"   Provider: {result['provider']}")
            print(f"   Audio Data Length: {len(result['audio_data'])} characters (base64)")
            return True
        else:
            print(f"❌ TTS Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def test_transcription_endpoint():
    """Test transcription endpoint with mock audio"""
    print("\n=== Testing Transcription Endpoint ===")
    
    try:
        # Create a small dummy audio file
        dummy_audio = b"dummy audio content for testing transcription"
        
        files = {"audio_file": ("test.wav", dummy_audio, "audio/wav")}
        data = {"provider": "openai"}
        
        response = requests.post(f"{BASE_URL}/api/v1/transcribe", files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Transcription Success:")
            print(f"   Transcript: {result['transcript']}")
            print(f"   Emotion Score: {result['emotion_analysis']['emotion_score']}")
            print(f"   Enthusiasm: {result['emotion_analysis']['enthusiasm_level']}")
            print(f"   Transcription Time: {result['transcription_time']:.2f}s")
            return True
        else:
            print(f"❌ Transcription Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Transcription test failed: {e}")
        return False

def test_full_conversation():
    """Test full conversation pipeline"""
    print("\n=== Testing Full Conversation Pipeline ===")
    
    try:
        # Create a dummy audio file
        dummy_audio = b"Hi, I'm looking for office space for my growing tech company. We need about 2500 square feet."
        
        files = {"audio_file": ("conversation.wav", dummy_audio, "audio/wav")}
        data = {
            "session_id": "test_session_001",
            "include_audio_response": "true"
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/converse", files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Full Conversation Pipeline Success:")
            print(f"   Transcript: {result['transcript']}")
            print(f"   Response: {result['response'][:100]}...")
            print(f"   Total Processing Time: {result['processing_times']['total_time']:.2f}s")
            print(f"   Session ID: {result['session_id']}")
            
            # Test conversation history
            history_response = requests.get(f"{BASE_URL}/api/v1/conversation-history/{result['session_id']}")
            if history_response.status_code == 200:
                history = history_response.json()
                print(f"   Conversation History: {history['message_count']} messages")
            
            return True
        else:
            print(f"❌ Conversation Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Full conversation test failed: {e}")
        return False

def test_document_upload():
    """Test document upload functionality"""
    print("\n=== Testing Document Upload ===")
    
    try:
        # Create a test document
        test_content = """
        Commercial Real Estate Market Report 2024
        
        The downtown tech district is experiencing high demand for modern office spaces.
        Companies are looking for collaborative workspaces with good natural light.
        Average rent is $28-35 per square foot annually.
        
        Popular amenities include:
        - High-speed internet
        - Conference rooms
        - Kitchen facilities
        - Parking
        """
        
        files = {"files": ("market_report.txt", test_content.encode(), "text/plain")}
        data = {"document_type": "market_research"}
        
        response = requests.post(f"{BASE_URL}/api/v1/upload_rag_docs", files=files, data=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Document Upload Success:")
            print(f"   Documents Processed: {result['documents_processed']}")
            print(f"   Processing Time: {result['processing_time']:.2f}s")
            
            # Test document search
            search_response = requests.post(f"{BASE_URL}/api/v1/rag_docs/search?query=downtown tech district&top_k=2")
            if search_response.status_code == 200:
                search_result = search_response.json()
                print(f"   Document Search: Found relevant context")
                print(f"   Context Preview: {search_result['context'][:100]}...")
            
            return True
        else:
            print(f"❌ Document Upload Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document upload test failed: {e}")
        return False

def test_property_matching():
    """Test property matching with conversation"""
    print("\n=== Testing Property Matching ===")
    
    try:
        # Test with specific requirements
        chat_data = {
            "message": "I need 2500 square feet for 20 employees in downtown. Budget is $30 per square foot. We're a creative tech company that values collaboration.",
            "conversation_history": [
                {"role": "user", "content": "Hi, I'm looking for office space"},
                {"role": "assistant", "content": "I'd be happy to help! Tell me about your requirements."}
            ],
            "emotion_data": {
                "enthusiasm_level": 0.7,
                "emotion_score": 0.8,
                "tone_analysis": {
                    "excited": 0.6,
                    "professional": 0.8,
                    "confident": 0.7
                }
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_data)
        if response.status_code == 200:
            result = response.json()
            response_text = result['response'].lower()
            
            # Check if response mentions properties
            property_keywords = ['property', 'space', 'square feet', 'rent', 'innovation', 'downtown']
            if any(keyword in response_text for keyword in property_keywords):
                print("✅ Property Matching Success:")
                print("   Response includes property recommendations")
                print(f"   Sample: {result['response'][:150]}...")
                return True
            else:
                print("⚠️  Property matching may not be working as expected")
                print(f"   Response: {result['response'][:100]}...")
                return False
        else:
            print(f"❌ Property Matching Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Property matching test failed: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("🚀 Testing Commercial Real Estate Voice AI API")
    print("=" * 60)
    
    tests = [
        ("Basic Endpoints", test_basic_endpoints),
        ("Chat Endpoint", test_chat_endpoint),
        ("Text-to-Speech", test_tts_endpoint),
        ("Transcription", test_transcription_endpoint),
        ("Document Upload", test_document_upload),
        ("Property Matching", test_property_matching),
        ("Full Conversation", test_full_conversation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1
    
    print(f"\nTests Passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Your API is working correctly.")
        print("📖 Visit http://localhost:8000/docs for interactive documentation")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("💡 Make sure your .env file has the correct API keys")

if __name__ == "__main__":
    run_all_tests()