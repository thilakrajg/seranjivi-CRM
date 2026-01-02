import requests

def test_api():
    url = "http://localhost:8000/api/leads"
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"API Response Status: {response.status_code}")
            print(f"Number of leads: {len(data)}")
            
            if data:
                sample_lead = data[0]
                print(f"\nSample lead fields:")
                for key, value in sample_lead.items():
                    if key in ['id', 'stage', 'status', 'lead_status']:
                        print(f"  {key}: {value}")
                        
                print(f"\nChecking for lead_status field:")
                print(f"  Has lead_status: {'lead_status' in sample_lead}")
                if 'lead_status' in sample_lead:
                    print(f"  lead_status value: {sample_lead['lead_status']}")
        else:
            print(f"API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_api()
