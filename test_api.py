"""
Test API Endpoints for MSME Financial Stress Score Advisor
Run this script to test all API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Print formatted response"""
    print(f"\n{'='*70}")
    print(f"📋 {title}")
    print(f"{'='*70}")
    print(f"Status: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_health():
    """Test health endpoints"""
    print("\n" + "="*70)
    print("🏥 HEALTH ENDPOINTS")
    print("="*70)
    
    # Root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print_response("GET /", response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response("GET /health", response)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_scores():
    """Test score endpoints"""
    print("\n" + "="*70)
    print("📊 STRESS SCORE ENDPOINTS")
    print("="*70)
    
    # Get all scores
    try:
        response = requests.get(f"{BASE_URL}/scores")
        print_response("GET /scores (All MSMEs)", response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(1)
    
    # Get specific MSME score
    try:
        response = requests.get(f"{BASE_URL}/scores/MSME001")
        print_response("GET /scores/MSME001 (Specific MSME)", response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(1)
    
    # Try non-existent MSME
    try:
        response = requests.get(f"{BASE_URL}/scores/NONEXISTENT")
        print_response("GET /scores/NONEXISTENT (Should return 404)", response)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_alerts():
    """Test alert endpoints"""
    print("\n" + "="*70)
    print("⚠️  ALERTS ENDPOINTS")
    print("="*70)
    
    # Default threshold (0.4)
    try:
        response = requests.get(f"{BASE_URL}/alerts")
        print_response("GET /alerts (Default threshold=0.4)", response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(1)
    
    # Custom threshold
    try:
        response = requests.get(f"{BASE_URL}/alerts?threshold=0.5")
        print_response("GET /alerts?threshold=0.5", response)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_transactions():
    """Test transaction simulation endpoint"""
    print("\n" + "="*70)
    print("💳 TRANSACTION SIMULATION ENDPOINT")
    print("="*70)
    
    # Add inflow transaction
    try:
        response = requests.post(
            f"{BASE_URL}/transactions",
            params={
                "msme_id": "MSME001",
                "amount": 75000,
                "type": "inflow",
                "category": "sales"
            }
        )
        print_response("POST /transactions (Inflow)", response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(2)  # Let pipeline process
    
    # Add outflow transaction
    try:
        response = requests.post(
            f"{BASE_URL}/transactions",
            params={
                "msme_id": "MSME001",
                "amount": 15000,
                "type": "outflow",
                "category": "rent"
            }
        )
        print_response("POST /transactions (Outflow)", response)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    time.sleep(2)  # Let pipeline process
    
    # Check updated score
    try:
        response = requests.get(f"{BASE_URL}/scores/MSME001")
        print_response("GET /scores/MSME001 (After transactions)", response)
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  MSME Financial Stress Score Advisor - API Test Suite".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    print(f"\n🔌 Base URL: {BASE_URL}")
    print("⏳ Make sure the server is running on http://localhost:8000")
    
    # Wait for server to be ready
    print("\n⏳ Checking server connectivity...")
    retries = 5
    while retries > 0:
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print("✅ Server is ready!\n")
            break
        except:
            retries -= 1
            if retries > 0:
                print(f"⏳ Waiting for server... ({retries} retries left)")
                time.sleep(2)
            else:
                print("❌ Server is not responding. Make sure it's running with: python main.py")
                return
    
    # Run tests
    test_health()
    time.sleep(1)
    
    test_scores()
    time.sleep(1)
    
    test_alerts()
    time.sleep(1)
    
    test_transactions()
    
    # Summary
    print("\n" + "="*70)
    print("✅ API TEST COMPLETE")
    print("="*70)
    print("\n📖 Full API Documentation available at: http://localhost:8000/docs")
    print("\n")

if __name__ == "__main__":
    main()
