import asyncio
import aiohttp
import json

async def test_api():
    url = "http://localhost:8000/api/leads"
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"API Response Status: {response.status}")
                    print(f"Number of leads: {len(data)}")
                    
                    if data:
                        sample_lead = data[0]
                        print(f"\nSample lead fields:")
                        for key, value in sample_lead.items():
                            print(f"  {key}: {value}")
                            
                        # Check specifically for status fields
                        print(f"\nStatus fields:")
                        print(f"  status: {sample_lead.get('status')}")
                        print(f"  lead_status: {sample_lead.get('lead_status')}")
                else:
                    print(f"API Error: {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())
