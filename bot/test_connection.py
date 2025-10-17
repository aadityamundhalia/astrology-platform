import asyncio
import asyncpg
from config import get_settings

async def test_connection():
    settings = get_settings()
    
    try:
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        
        version = await conn.fetchval('SELECT version()')
        print(f"✅ Connected to PostgreSQL!")
        print(f"Version: {version}")
        
        # Check if users table exists
        exists = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')"
        )
        print(f"✅ Users table exists: {exists}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
