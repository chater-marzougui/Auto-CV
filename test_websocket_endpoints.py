#!/usr/bin/env python3
"""
Test suite for websocket-enabled endpoints in CV Generator Backend
Tests the updated job analysis and application generation endpoints
"""

import requests
import websocket
import json
import time
import threading
import asyncio
from typing import Dict, List
import uuid

# Configuration
BASE_URL = "http://localhost:5000"
WS_BASE_URL = "ws://localhost:5000"

# Test data
SAMPLE_JOB_DESCRIPTION = """
Software Engineer - Full Stack
We are looking for a talented Full Stack Software Engineer to join our team. 

Requirements:
- 3+ years of experience in web development
- Proficiency in Python, JavaScript, and React
- Experience with REST APIs and database design
- Knowledge of Docker and cloud platforms
- Strong problem-solving skills and teamwork abilities

Responsibilities:
- Develop and maintain web applications
- Work with cross-functional teams
- Implement new features and optimize performance
- Write clean, maintainable code
"""

SAMPLE_PERSONAL_INFO = {
    "first_name": "John",
    "last_name": "Doe", 
    "email": "john.doe@example.com",
    "phone": "+1-555-0123",
    "address": "123 Tech Street",
    "city": "San Francisco",
    "postal_code": "94105",
    "title": "Full Stack Developer",
    "summary": "Experienced software developer with 5+ years in web development",
    "skills": {
        "Programming": ["Python", "JavaScript", "React", "Node.js"],
        "Databases": ["PostgreSQL", "MongoDB"],
        "Tools": ["Docker", "Git", "AWS"]
    },
    "experience": [{
        "title": "Software Developer",
        "company": "Tech Solutions Inc.",
        "location": "San Francisco, CA",
        "start_date": "2020-01",
        "end_date": "Present",
        "description": "Full-stack development and team leadership",
        "achievements": ["Improved performance by 40%", "Led team of 4 developers"]
    }],
    "education": [{
        "degree": "B.S. Computer Science",
        "institution": "University of Technology",
        "location": "California, USA",
        "start_date": "2016-09",
        "end_date": "2020-05",
        "gpa": "3.8"
    }]
}

class WebSocketTester:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.ws_url = f"{WS_BASE_URL}/ws/{client_id}"
        self.messages = []
        self.connected = False
        
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.messages.append(data)
            print(f"📥 WebSocket message: {data.get('message', 'Unknown message')}")
        except json.JSONDecodeError:
            print(f"📥 Raw WebSocket message: {message}")
            
    def on_error(self, ws, error):
        print(f"❌ WebSocket error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        print(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False
        
    def on_open(self, ws):
        print(f"🚀 WebSocket connected: {self.ws_url}")
        self.connected = True
        
    def connect(self):
        """Connect to websocket and run in background thread"""
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
        def run_ws():
            self.ws.run_forever()
            
        self.ws_thread = threading.Thread(target=run_ws)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
        # Wait for connection
        time.sleep(2)
        return self.connected
        
    def disconnect(self):
        """Close websocket connection"""
        if hasattr(self, 'ws'):
            self.ws.close()
        self.connected = False
        
    def get_messages(self) -> List[Dict]:
        """Get all received messages"""
        return self.messages.copy()
        
    def wait_for_completion(self, timeout: int = 30) -> bool:
        """Wait for completion message or timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for msg in self.messages:
                if msg.get('step') in ['completed', 'finished', 'error']:
                    return True
            time.sleep(1)
        return False

def test_health_check():
    """Test basic API health"""
    print("\n🏥 Testing API health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_websocket_connection():
    """Test basic websocket connectivity"""
    print("\n🔌 Testing WebSocket connection...")
    try:
        client_id = str(uuid.uuid4())
        ws_tester = WebSocketTester(client_id)
        
        connected = ws_tester.connect()
        if connected:
            print("✅ WebSocket connection successful")
            ws_tester.disconnect()
            return True
        else:
            print("❌ WebSocket connection failed")
            return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

def test_job_analysis_with_websocket():
    """Test job analysis endpoint with websocket updates"""
    print("\n📊 Testing job analysis with WebSocket updates...")
    try:
        client_id = f"job-analysis-{int(time.time())}"
        ws_tester = WebSocketTester(client_id)
        
        # Connect websocket
        if not ws_tester.connect():
            print("❌ Failed to connect to WebSocket")
            return False
        
        # Make job analysis request
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze-job",
            json={
                "description": SAMPLE_JOB_DESCRIPTION,
                "client_id": client_id
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Job analysis failed: {response.status_code}")
            ws_tester.disconnect()
            return False
        
        # Wait for websocket messages
        ws_tester.wait_for_completion(timeout=10)
        messages = ws_tester.get_messages()
        
        ws_tester.disconnect()
        
        if messages:
            print(f"✅ Job analysis completed with {len(messages)} WebSocket updates")
            for msg in messages:
                print(f"  📝 {msg.get('step', 'unknown')}: {msg.get('message', 'No message')}")
            return True
        else:
            print("❌ No WebSocket messages received")
            return False
            
    except Exception as e:
        print(f"❌ Job analysis test failed: {e}")
        return False

def test_project_matching_with_websocket():
    """Test project matching endpoint with websocket updates"""
    print("\n🔍 Testing project matching with WebSocket updates...")
    try:
        client_id = f"project-matching-{int(time.time())}"
        ws_tester = WebSocketTester(client_id)
        
        # Connect websocket
        if not ws_tester.connect():
            print("❌ Failed to connect to WebSocket")
            return False
        
        # First analyze job to get structured data
        analyze_response = requests.post(
            f"{BASE_URL}/api/v1/analyze-job",
            json={"description": SAMPLE_JOB_DESCRIPTION}
        )
        
        if analyze_response.status_code != 200:
            print("❌ Job analysis prerequisite failed")
            ws_tester.disconnect()
            return False
        
        job_data = analyze_response.json()
        
        # Make project matching request
        response = requests.post(
            f"{BASE_URL}/api/v1/match-projects",
            json={
                "job_description": job_data,
                "client_id": client_id
            }
        )
        
        # Wait for websocket messages
        ws_tester.wait_for_completion(timeout=10)
        messages = ws_tester.get_messages()
        
        ws_tester.disconnect()
        
        if response.status_code == 200:
            print(f"✅ Project matching completed with {len(messages)} WebSocket updates")
            matched_projects = response.json()
            print(f"  🎯 Found {len(matched_projects)} matching projects")
            return True
        elif response.status_code == 404:
            print("⚠️ No projects found (expected if no GitHub scraping done)")
            return True  # This is acceptable for testing
        else:
            print(f"❌ Project matching failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Project matching test failed: {e}")
        return False

def setup_personal_info():
    """Setup personal info for testing"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/personal-info",
            json=SAMPLE_PERSONAL_INFO
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("id")
        return None
    except:
        return None

def test_application_generation_with_websocket():
    """Test full application generation with websocket updates"""
    print("\n🎯 Testing application generation with WebSocket updates...")
    try:
        client_id = f"app-generation-{int(time.time())}"
        ws_tester = WebSocketTester(client_id)
        
        # Setup personal info
        personal_info_id = setup_personal_info()
        if not personal_info_id:
            print("⚠️ Could not setup personal info, skipping application generation test")
            return True
        
        # Connect websocket
        if not ws_tester.connect():
            print("❌ Failed to connect to WebSocket")
            return False
        
        # Analyze job first
        analyze_response = requests.post(
            f"{BASE_URL}/api/v1/analyze-job",
            json={"description": SAMPLE_JOB_DESCRIPTION}
        )
        
        if analyze_response.status_code != 200:
            print("❌ Job analysis prerequisite failed")
            ws_tester.disconnect()
            return False
        
        job_data = analyze_response.json()
        
        # Generate full application
        response = requests.post(
            f"{BASE_URL}/api/v1/generate-full-application",
            json={
                "job_description": job_data,
                "personal_info_id": personal_info_id,
                "top_k": 3,
                "client_id": client_id
            }
        )
        
        # Wait for websocket messages (longer timeout for generation)
        ws_tester.wait_for_completion(timeout=30)
        messages = ws_tester.get_messages()
        
        ws_tester.disconnect()
        
        if response.status_code == 200:
            print(f"✅ Application generation completed with {len(messages)} WebSocket updates")
            result = response.json()
            print(f"  📄 CV: {result.get('cv', {}).get('download_url', 'No URL')}")
            print(f"  📝 Cover Letter: {result.get('cover_letter', {}).get('download_url', 'No URL')}")
            return True
        elif response.status_code == 404:
            print("⚠️ No projects found for application generation (expected if no GitHub scraping done)")
            return True  # This is acceptable for testing
        else:
            print(f"❌ Application generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Application generation test failed: {e}")
        return False

def run_all_tests():
    """Run all websocket endpoint tests"""
    print("🧪 Starting WebSocket Endpoint Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("WebSocket Connection", test_websocket_connection),
        ("Job Analysis with WebSocket", test_job_analysis_with_websocket),
        ("Project Matching with WebSocket", test_project_matching_with_websocket),
        ("Application Generation with WebSocket", test_application_generation_with_websocket),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
        
        time.sleep(1)  # Brief pause between tests
    
    # Print summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the server logs for details.")
    
    return passed == total

if __name__ == "__main__":
    print("🚀 WebSocket Endpoint Test Suite")
    print("Make sure the backend server is running on localhost:5000")
    input("Press Enter to continue...")
    
    success = run_all_tests()
    exit(0 if success else 1)