#!/usr/bin/env python3
"""
Comprehensive Backend Testing for ChatPDF Application
Tests all API endpoints and functionality as specified in test_result.md
"""

import asyncio
import aiohttp
import json
import io
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

# Backend URL from frontend/.env
BACKEND_URL = "https://20f35a5c-6b48-421b-af0b-9bb6afed2668.preview.emergentagent.com"
API_BASE_URL = f"{BACKEND_URL}/api"

class ChatPDFTester:
    def __init__(self):
        self.session = None
        self.test_session_id = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_health_endpoints(self):
        """Test health check endpoints"""
        print("🏥 Testing Health Endpoints...")
        
        # Basic health check
        try:
            async with self.session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Basic Health Check", True, f"Status: {data.get('status')}")
                else:
                    self.log_test("Basic Health Check", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Basic Health Check", False, f"Exception: {str(e)}")
        
        # System health check
        try:
            async with self.session.get(f"{API_BASE_URL}/system-health") as response:
                if response.status == 200:
                    data = await response.json()
                    overall_status = data.get('overall_status', 'unknown')
                    backend_status = data.get('backend_status', 'unknown')
                    self.log_test("System Health Check", True, 
                                f"Overall: {overall_status}, Backend: {backend_status}")
                else:
                    self.log_test("System Health Check", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("System Health Check", False, f"Exception: {str(e)}")
        
        # Health metrics
        try:
            async with self.session.get(f"{API_BASE_URL}/system-health/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    uptime = data.get('uptime', 0)
                    self.log_test("Health Metrics", True, f"Uptime: {uptime:.2f}s")
                else:
                    self.log_test("Health Metrics", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Health Metrics", False, f"Exception: {str(e)}")
    
    async def test_models_endpoint(self):
        """Test available AI models endpoint"""
        print("🤖 Testing AI Models Endpoint...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/models") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('models', [])
                    model_count = len(models)
                    
                    # Check for expected providers
                    providers = set(model.get('provider', '') for model in models)
                    
                    self.log_test("AI Models Endpoint", True, 
                                f"Found {model_count} models from providers: {', '.join(providers)}")
                    
                    # Log individual models
                    for model in models[:5]:  # Show first 5 models
                        print(f"   - {model.get('name', 'Unknown')} ({model.get('provider', 'Unknown')})")
                else:
                    self.log_test("AI Models Endpoint", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("AI Models Endpoint", False, f"Exception: {str(e)}")
    
    async def test_session_management(self):
        """Test session creation, listing, and deletion"""
        print("📝 Testing Session Management...")
        
        # Create session
        try:
            session_data = {"title": "Test Session for Backend Testing"}
            async with self.session.post(f"{API_BASE_URL}/sessions", 
                                       json=session_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.test_session_id = data.get('id')
                    self.log_test("Create Session", True, f"Session ID: {self.test_session_id}")
                else:
                    self.log_test("Create Session", False, f"HTTP {response.status}")
                    return
        except Exception as e:
            self.log_test("Create Session", False, f"Exception: {str(e)}")
            return
        
        # List sessions
        try:
            async with self.session.get(f"{API_BASE_URL}/sessions") as response:
                if response.status == 200:
                    sessions = await response.json()
                    session_count = len(sessions)
                    self.log_test("List Sessions", True, f"Found {session_count} sessions")
                else:
                    self.log_test("List Sessions", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("List Sessions", False, f"Exception: {str(e)}")
    
    async def test_supported_formats(self):
        """Test supported document formats endpoint"""
        print("📄 Testing Supported Formats...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/supported-formats") as response:
                if response.status == 200:
                    data = await response.json()
                    formats = data.get('supported_formats', [])
                    self.log_test("Supported Formats", True, 
                                f"Supports: {', '.join(formats)}")
                else:
                    self.log_test("Supported Formats", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Supported Formats", False, f"Exception: {str(e)}")
    
    async def test_document_upload(self):
        """Test document upload functionality"""
        print("📤 Testing Document Upload...")
        
        if not self.test_session_id:
            self.log_test("Document Upload", False, "No test session available")
            return
        
        # Create a simple test PDF content
        test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF for ChatPDF Backend Testing) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
0000000185 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
279
%%EOF"""
        
        # Test universal document upload endpoint
        try:
            data = aiohttp.FormData()
            data.add_field('file', test_pdf_content, 
                          filename='test_document.pdf', 
                          content_type='application/pdf')
            
            async with self.session.post(
                f"{API_BASE_URL}/sessions/{self.test_session_id}/upload-document",
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    filename = result.get('filename', 'unknown')
                    file_type = result.get('file_type', 'unknown')
                    content_length = result.get('content_length', 0)
                    self.log_test("Universal Document Upload", True, 
                                f"Uploaded {filename} ({file_type}), {content_length} chars extracted")
                else:
                    response_text = await response.text()
                    self.log_test("Universal Document Upload", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Universal Document Upload", False, f"Exception: {str(e)}")
        
        # Test legacy PDF upload endpoint for backward compatibility
        try:
            data = aiohttp.FormData()
            data.add_field('file', test_pdf_content, 
                          filename='test_legacy.pdf', 
                          content_type='application/pdf')
            
            async with self.session.post(
                f"{API_BASE_URL}/sessions/{self.test_session_id}/upload-pdf",
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    self.log_test("Legacy PDF Upload", True, 
                                f"Backward compatibility working")
                else:
                    self.log_test("Legacy PDF Upload", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Legacy PDF Upload", False, f"Exception: {str(e)}")
    
    async def test_chat_functionality(self):
        """Test chat functionality with AI integration"""
        print("💬 Testing Chat Functionality...")
        
        if not self.test_session_id:
            self.log_test("Chat Functionality", False, "No test session available")
            return
        
        # Test general AI chat
        try:
            chat_data = {
                "session_id": self.test_session_id,
                "content": "Hello! Can you tell me what 2+2 equals?",
                "model": "claude-3-haiku-20240307",
                "feature_type": "general_ai"
            }
            
            async with self.session.post(f"{API_BASE_URL}/sessions/{self.test_session_id}/messages",
                                       json=chat_data) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result.get('ai_response', {})
                    content = ai_response.get('content', '')[:100]
                    self.log_test("General AI Chat", True, 
                                f"AI responded: {content}...")
                else:
                    response_text = await response.text()
                    self.log_test("General AI Chat", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("General AI Chat", False, f"Exception: {str(e)}")
        
        # Test document-based chat
        try:
            chat_data = {
                "session_id": self.test_session_id,
                "content": "What is this document about?",
                "model": "claude-3-haiku-20240307",
                "feature_type": "chat"
            }
            
            async with self.session.post(f"{API_BASE_URL}/sessions/{self.test_session_id}/messages",
                                       json=chat_data) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result.get('ai_response', {})
                    content = ai_response.get('content', '')[:100]
                    self.log_test("Document Chat", True, 
                                f"AI responded: {content}...")
                else:
                    response_text = await response.text()
                    self.log_test("Document Chat", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Document Chat", False, f"Exception: {str(e)}")
    
    async def test_question_generation(self):
        """Test Q&A generation feature"""
        print("❓ Testing Question Generation...")
        
        if not self.test_session_id:
            self.log_test("Question Generation", False, "No test session available")
            return
        
        try:
            qa_data = {
                "session_id": self.test_session_id,
                "question_type": "mixed",
                "model": "claude-3-haiku-20240307"
            }
            
            async with self.session.post(f"{API_BASE_URL}/generate-questions",
                                       json=qa_data) as response:
                if response.status == 200:
                    result = await response.json()
                    questions = result.get('questions', [])
                    self.log_test("Question Generation", True, 
                                f"Generated {len(questions)} questions")
                else:
                    response_text = await response.text()
                    self.log_test("Question Generation", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Question Generation", False, f"Exception: {str(e)}")
    
    async def test_research_features(self):
        """Test research and summary features (via chat with research feature_type)"""
        print("🔬 Testing Research Features...")
        
        if not self.test_session_id:
            self.log_test("Research Features", False, "No test session available")
            return
        
        # Test research via chat with research feature_type
        try:
            research_data = {
                "session_id": self.test_session_id,
                "content": "Please provide a summary of the uploaded document",
                "model": "claude-3-haiku-20240307",
                "feature_type": "research"
            }
            
            async with self.session.post(f"{API_BASE_URL}/sessions/{self.test_session_id}/messages",
                                       json=research_data) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result.get('ai_response', {})
                    content = ai_response.get('content', '')[:100]
                    self.log_test("Research via Chat", True, 
                                f"Research response: {content}...")
                else:
                    response_text = await response.text()
                    self.log_test("Research via Chat", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Research via Chat", False, f"Exception: {str(e)}")
    
    async def test_translation_feature(self):
        """Test PDF translation feature"""
        print("🌐 Testing Translation Feature...")
        
        if not self.test_session_id:
            self.log_test("Translation Feature", False, "No test session available")
            return
        
        try:
            translate_data = {
                "session_id": self.test_session_id,
                "target_language": "Spanish",
                "content_type": "summary",
                "model": "claude-3-haiku-20240307"
            }
            
            async with self.session.post(f"{API_BASE_URL}/translate",
                                       json=translate_data) as response:
                if response.status == 200:
                    result = await response.json()
                    translation = result.get('translation', '')[:100]
                    self.log_test("Translation Feature", True, 
                                f"Translated to Spanish: {translation}...")
                else:
                    response_text = await response.text()
                    self.log_test("Translation Feature", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Translation Feature", False, f"Exception: {str(e)}")
    
    async def test_search_functionality(self):
        """Test advanced search functionality"""
        print("🔍 Testing Search Functionality...")
        
        try:
            search_data = {
                "query": "test document",
                "search_type": "all",
                "limit": 10
            }
            
            async with self.session.post(f"{API_BASE_URL}/search",
                                       json=search_data) as response:
                if response.status == 200:
                    result = await response.json()
                    results = result.get('results', [])
                    self.log_test("Advanced Search", True, 
                                f"Found {len(results)} search results")
                else:
                    response_text = await response.text()
                    self.log_test("Advanced Search", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Advanced Search", False, f"Exception: {str(e)}")
    
    async def test_export_functionality(self):
        """Test conversation export functionality"""
        print("📥 Testing Export Functionality...")
        
        if not self.test_session_id:
            self.log_test("Export Functionality", False, "No test session available")
            return
        
        # Test different export formats using POST endpoint
        for export_format in ["txt", "pdf", "docx"]:
            try:
                export_data = {
                    "session_id": self.test_session_id,
                    "export_format": export_format,
                    "include_messages": True
                }
                
                async with self.session.post(f"{API_BASE_URL}/export",
                                           json=export_data) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        self.log_test(f"Export {export_format.upper()}", True, 
                                    f"Content-Type: {content_type}")
                    else:
                        response_text = await response.text()
                        self.log_test(f"Export {export_format.upper()}", False, 
                                    f"HTTP {response.status}: {response_text}")
            except Exception as e:
                self.log_test(f"Export {export_format.upper()}", False, f"Exception: {str(e)}")
    
    async def test_insights_dashboard(self):
        """Test insights dashboard functionality"""
        print("📊 Testing Insights Dashboard...")
        
        try:
            async with self.session.get(f"{API_BASE_URL}/insights") as response:
                if response.status == 200:
                    result = await response.json()
                    stats = result.get('usage_stats', {})
                    total_sessions = stats.get('total_sessions', 0)
                    self.log_test("Insights Dashboard", True, 
                                f"Total sessions: {total_sessions}")
                else:
                    response_text = await response.text()
                    self.log_test("Insights Dashboard", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Insights Dashboard", False, f"Exception: {str(e)}")
    
    async def test_message_retrieval(self):
        """Test message retrieval functionality"""
        print("📨 Testing Message Retrieval...")
        
        if not self.test_session_id:
            self.log_test("Message Retrieval", False, "No test session available")
            return
        
        try:
            async with self.session.get(
                f"{API_BASE_URL}/sessions/{self.test_session_id}/messages"
            ) as response:
                if response.status == 200:
                    messages = await response.json()
                    message_count = len(messages)
                    self.log_test("Message Retrieval", True, 
                                f"Retrieved {message_count} messages")
                else:
                    response_text = await response.text()
                    self.log_test("Message Retrieval", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Message Retrieval", False, f"Exception: {str(e)}")
    
    async def cleanup_test_session(self):
        """Clean up test session"""
        print("🧹 Cleaning up test session...")
        
        if not self.test_session_id:
            return
        
        try:
            async with self.session.delete(
                f"{API_BASE_URL}/sessions/{self.test_session_id}"
            ) as response:
                if response.status == 200:
                    self.log_test("Session Cleanup", True, "Test session deleted")
                else:
                    self.log_test("Session Cleanup", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_test("Session Cleanup", False, f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Comprehensive ChatPDF Backend Testing")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"📡 API Base URL: {API_BASE_URL}")
        print("=" * 60)
        
        # Run all test suites
        await self.test_health_endpoints()
        await self.test_models_endpoint()
        await self.test_session_management()
        await self.test_supported_formats()
        await self.test_document_upload()
        await self.test_chat_functionality()
        await self.test_question_generation()
        await self.test_research_features()
        await self.test_translation_feature()
        await self.test_search_functionality()
        await self.test_export_functionality()
        await self.test_insights_dashboard()
        await self.test_message_retrieval()
        await self.cleanup_test_session()
        
        # Print summary
        print("=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
        
        print("\n🎯 Testing completed!")
        return passed, total

async def main():
    """Main test runner"""
    async with ChatPDFTester() as tester:
        passed, total = await tester.run_all_tests()
        
        # Exit with appropriate code
        if passed == total:
            print("🎉 All tests passed!")
            sys.exit(0)
        else:
            print(f"⚠️  {total - passed} tests failed!")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())