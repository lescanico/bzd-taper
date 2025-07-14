#!/usr/bin/env python3
"""
Test script for BZD Taper Generator Web App
"""

import requests
import json
from datetime import date

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing BZD Taper Generator Web App...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Main page: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python app.py")
        return False
    
    # Test 2: Get medications
    try:
        response = requests.get(f"{base_url}/api/medications")
        medications = response.json()
        print(f"✅ Medications API: {len(medications)} medications found")
        print(f"   Available: {', '.join(medications)}")
    except Exception as e:
        print(f"❌ Medications API failed: {e}")
        return False
    
    # Test 3: Get taper speeds
    try:
        response = requests.get(f"{base_url}/api/taper_speeds")
        speeds = response.json()
        print(f"✅ Taper speeds API: {len(speeds)} speeds available")
        for speed, details in speeds.items():
            print(f"   {speed}: {details['percent']}% every {details['interval_days']} days")
    except Exception as e:
        print(f"❌ Taper speeds API failed: {e}")
        return False
    
    # Test 4: Get strengths for a medication
    try:
        response = requests.get(f"{base_url}/api/strengths/diazepam")
        strengths = response.json()
        print(f"✅ Strengths API: {len(strengths)} strengths for diazepam")
        print(f"   Available: {', '.join(map(str, strengths))} mg")
    except Exception as e:
        print(f"❌ Strengths API failed: {e}")
        return False
    
    # Test 5: Generate a taper plan
    try:
        test_data = {
            "medication": "clonazepam",
            "dose": 1.0,
            "speed": "standard",
            "start_date": date.today().isoformat(),
            "frequency": "auto"
        }
        
        response = requests.post(
            f"{base_url}/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ Taper generation: Success")
                print(f"   Total days: {result['total_days']}")
                print(f"   Steps: {len(result['plan'])}")
                print(f"   Patient instructions: {len(result['patient_instructions'])} lines")
            else:
                print(f"❌ Taper generation failed: {result.get('error')}")
                return False
        else:
            print(f"❌ Taper generation HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Taper generation failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Web app is working correctly.")
    return True

if __name__ == "__main__":
    success = test_api_endpoints()
    if success:
        print("\n🌐 Web app is ready! Open http://localhost:5000 in your browser.")
    else:
        print("\n❌ Some tests failed. Check the server logs.") 