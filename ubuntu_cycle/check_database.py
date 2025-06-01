import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import from main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import DBItem, SessionLocal, ItemStatusEnum

def check_database():
    """Check what items are currently in the database"""
    
    db = SessionLocal()
    try:
        items = db.query(DBItem).order_by(DBItem.date_posted.desc()).all()
        
        if not items:
            print("No items found in the database.")
            return
        
        print(f"Found {len(items)} items in the database:\n")
        print("=" * 80)
        
        for item in items:
            print(f"Title: {item.title}")
            print(f"Category: {item.category or 'No category'}")
            print(f"Status: {item.status}")
            if item.claimed_by_note:
                print(f"Claimed by: {item.claimed_by_note}")
            description = item.description or ""
            print(f"Description: {description[:100]}{'...' if len(description) > 100 else ''}")
            print(f"Posted: {item.date_posted.strftime('%Y-%m-%d %H:%M')}")
            print("-" * 80)
        
        # Summary by status
        print("\nSummary by Status:")
        available_count = sum(1 for item in items if item.status == ItemStatusEnum.AVAILABLE.value)
        claimed_count = sum(1 for item in items if item.status == ItemStatusEnum.CLAIMED.value)
        gone_count = sum(1 for item in items if item.status == ItemStatusEnum.GONE.value)
        
        print(f"Available: {available_count}")
        print(f"Claimed: {claimed_count}")
        print(f"Gone: {gone_count}")
        
        # Summary by category
        print("\nSummary by Category:")
        categories = {}
        for item in items:
            category = item.category or "No category"
            categories[category] = categories.get(category, 0) + 1
        
        for category, count in sorted(categories.items()):
            print(f"{category}: {count}")
            
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database()