"""
MongoDB Database Setup Module
Can be run standalone or imported into app.py
"""

from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import certifi

# Load environment variables
load_dotenv()

def get_mongo_client():
    """Get MongoDB client connection with proper SSL configuration"""
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    
    # Configure client with SSL settings using certifi
    client = MongoClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        retryWrites=True,
        w='majority'
    )
    return client

def clear_collections(db):
    """Clear all data from collections"""
    print("🗑️  Clearing existing data...")
    db['tasks'].delete_many({})
    db['users'].delete_many({})
    print("✅ Collections cleared")

def create_sample_tasks(tasks_collection):
    """Insert sample tasks into database"""
    print("📝 Inserting sample tasks...")
    sample_tasks = [
        {
            "title": "Learn Python Basics",
            "completed": True,
            "created_at": datetime.now().isoformat(),
            "priority": "high",
            "description": "Complete Python fundamentals course"
        },
        {
            "title": "Build Flask API",
            "completed": True,
            "created_at": datetime.now().isoformat(),
            "priority": "high",
            "description": "Create REST API with Flask and MongoDB"
        },
        {
            "title": "Deploy to Render",
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "priority": "medium",
            "description": "Deploy application to cloud platform"
        },
        {
            "title": "Learn MongoDB",
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "priority": "medium",
            "description": "Understand NoSQL databases and MongoDB operations"
        },
        {
            "title": "Create Frontend UI",
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "priority": "low",
            "description": "Build interactive web interface with HTML/CSS/JS"
        }
    ]
    
    result = tasks_collection.insert_many(sample_tasks)
    print(f"✅ Inserted {len(result.inserted_ids)} tasks")
    return len(result.inserted_ids)

def create_sample_users(users_collection):
    """Insert sample users into database"""
    print("👥 Inserting sample users...")
    sample_users = [
        {
            "name": "Thakur Paudel",
            "email": "thakur@example.com",
            "role": "admin",
            "created_at": datetime.now().isoformat()
        },
        {
            "name": "Demo User",
            "email": "demo@example.com",
            "role": "user",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    result = users_collection.insert_many(sample_users)
    print(f"✅ Inserted {len(result.inserted_ids)} users")
    return len(result.inserted_ids)

def create_indexes(db):
    """Create database indexes for better performance"""
    print("🔍 Creating indexes...")
    db['tasks'].create_index("created_at")
    db['tasks'].create_index("completed")
    db['users'].create_index("email", unique=True)
    print("✅ Indexes created")

def display_summary(db):
    """Display database summary"""
    print("\n" + "="*50)
    print("📊 DATABASE SUMMARY")
    print("="*50)
    print(f"Database: flask_db")
    print(f"Collections created: {len(db.list_collection_names())}")
    print(f"\nCollections:")
    for collection_name in db.list_collection_names():
        count = db[collection_name].count_documents({})
        print(f"  - {collection_name}: {count} documents")
    
    print("\n✨ Sample task:")
    first_task = db['tasks'].find_one()
    if first_task:
        print(f"  Title: {first_task['title']}")
        print(f"  Completed: {first_task['completed']}")
        print(f"  Priority: {first_task.get('priority', 'N/A')}")
        print(f"  ID: {first_task['_id']}")
    
    print("\n" + "="*50)

def check_database_empty(db):
    """Check if database has any data"""
    tasks_count = db['tasks'].count_documents({})
    users_count = db['users'].count_documents({})
    return tasks_count == 0 and users_count == 0

def setup_database(auto_populate=True):
    """
    Main setup function
    
    Args:
        auto_populate (bool): If True, automatically adds sample data
        
    Returns:
        bool: True if setup successful, False otherwise
    """
    
    print("🔗 Connecting to MongoDB...")
    try:
        client = get_mongo_client()
        # Test connection
        client.server_info()
        print("✅ Connected to MongoDB successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print("\n💡 Make sure:")
        print("   1. MongoDB Atlas cluster is running")
        print("   2. MONGO_URI is set in .env file")
        print("   3. Network access is configured (0.0.0.0/0)")
        return False
    
    # Get database
    db = client['flask_db']
    print(f"📊 Using database: flask_db")
    
    if auto_populate:
        # Clear existing data
        clear_collections(db)
        
        # Create sample data
        create_sample_tasks(db['tasks'])
        create_sample_users(db['users'])
        
        # Create indexes
        create_indexes(db)
        
        # Display summary
        display_summary(db)
        
        print("\n🎉 Database setup completed successfully!")
        print("="*50)
        print("\n💡 Next steps:")
        print("   1. Run: python app.py")
        print("   2. Open: http://localhost:5001")
        print("   3. Test the API endpoints")
    else:
        print("📊 Database connection established")
        print(f"   Tasks: {db['tasks'].count_documents({})} documents")
        print(f"   Users: {db['users'].count_documents({})} documents")
    
    client.close()
    return True

def init_database_if_empty(db):
    """
    Initialize database with sample data only if it's empty
    Called automatically by app.py on startup
    
    Args:
        db: MongoDB database object
    """
    if check_database_empty(db):
        print("\n" + "="*50)
        print("🔄 Database is empty - initializing with sample data...")
        print("="*50)
        create_sample_tasks(db['tasks'])
        create_sample_users(db['users'])
        create_indexes(db)
        print("✅ Database initialized!")
        print("="*50 + "\n")
    else:
        print("✅ Database already has data")

if __name__ == "__main__":
    print("="*50)
    print("🍃 MONGODB DATABASE SETUP")
    print("="*50)
    setup_database(auto_populate=True)