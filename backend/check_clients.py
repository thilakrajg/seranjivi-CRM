import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_clients():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['sales_crm']
    
    # Count total clients
    count = await db.clients.count_documents({})
    print(f'Total clients in DB: {count}')
    
    # Get all client names
    docs = await db.clients.find({}, {'_id': 0, 'client_name': 1}).to_list(20)
    print('Client names:', [doc.get('client_name', 'No name') for doc in docs])
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_clients())
