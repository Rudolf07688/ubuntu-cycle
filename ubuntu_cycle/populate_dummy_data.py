import os
import sys
from datetime import datetime, timedelta
import random

# Add the parent directory to the path so we can import from main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import DBItem, SessionLocal, ItemStatusEnum

def create_dummy_items():
    """Create realistic dummy items for the UbuntuCycle database"""
    
    # Sample data for realistic items
    items_data = [
        {
            "title": "Vintage Wooden Coffee Table",
            "description": "Beautiful solid wood coffee table with minor scratches. Perfect for a cozy living room. Dimensions: 120cm x 60cm x 45cm",
            "category": "Furniture",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Children's Bicycle (Age 5-8)",
            "description": "Red and blue kids bike with training wheels included. Some rust on the chain but still functional. Great for learning!",
            "category": "Sports & Recreation",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Set of 6 Dinner Plates",
            "description": "White ceramic dinner plates, barely used. One small chip on one plate but otherwise in excellent condition.",
            "category": "Kitchen & Dining",
            "status": ItemStatusEnum.CLAIMED.value,
            "claimed_by_note": "Sarah M. - picking up this weekend"
        },
        {
            "title": "HP Laptop (2019 Model)",
            "description": "HP Pavilion laptop, 8GB RAM, 256GB SSD. Battery life is reduced but works fine when plugged in. Includes charger.",
            "category": "Electronics",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Garden Tools Set",
            "description": "Collection of garden tools: spade, rake, hoe, and hand trowel. Some wear but all functional. Perfect for spring gardening!",
            "category": "Garden & Outdoor",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Baby Stroller",
            "description": "Lightweight baby stroller, suitable for infants to toddlers. Easy to fold and transport. Clean and well-maintained.",
            "category": "Baby & Kids",
            "status": ItemStatusEnum.GONE.value
        },
        {
            "title": "Stack of Programming Books",
            "description": "Collection of 8 programming books including Python, JavaScript, and web development. Some highlighting but all pages intact.",
            "category": "Books & Media",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Winter Coat (Size M)",
            "description": "Warm winter coat, navy blue, size medium. Waterproof and in good condition. Perfect for the upcoming cold season.",
            "category": "Clothing",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Desk Lamp with LED Bulb",
            "description": "Adjustable desk lamp with energy-efficient LED bulb. Black metal finish, perfect for home office or study area.",
            "category": "Home & Office",
            "status": ItemStatusEnum.CLAIMED.value,
            "claimed_by_note": "Alex K. - will collect tomorrow evening"
        },
        {
            "title": "Yoga Mat and Blocks",
            "description": "Purple yoga mat (6mm thick) with two foam blocks. Lightly used, clean and ready for your next yoga session.",
            "category": "Sports & Recreation",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Microwave Oven",
            "description": "Samsung microwave, 800W, works perfectly. Moving house and can't take it with us. Includes manual.",
            "category": "Appliances",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Potted Plants (3 varieties)",
            "description": "Three healthy houseplants: snake plant, pothos, and rubber tree. Includes pots. Great for beginners!",
            "category": "Garden & Outdoor",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Board Game Collection",
            "description": "5 board games: Monopoly, Scrabble, Risk, Catan, and Ticket to Ride. All complete with pieces. Family game night ready!",
            "category": "Toys & Games",
            "status": ItemStatusEnum.CLAIMED.value,
            "claimed_by_note": "The Johnson Family - picking up this Saturday"
        },
        {
            "title": "Electric Kettle",
            "description": "Stainless steel electric kettle, 1.7L capacity. Fast boiling, automatic shut-off. Some limescale but easily cleaned.",
            "category": "Kitchen & Dining",
            "status": ItemStatusEnum.AVAILABLE.value
        },
        {
            "title": "Acoustic Guitar",
            "description": "Yamaha acoustic guitar, great for beginners. A few small dings but sounds beautiful. Includes soft case.",
            "category": "Musical Instruments",
            "status": ItemStatusEnum.AVAILABLE.value
        }
    ]
    
    db = SessionLocal()
    try:
        # Check if we already have items in the database
        existing_count = db.query(DBItem).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} items.")
            response = input("Do you want to add more dummy items anyway? (y/n): ")
            if response.lower() != 'y':
                print("Skipping dummy data creation.")
                return
        
        # Create items with varied posting dates (last 30 days)
        base_date = datetime.utcnow()
        
        for i, item_data in enumerate(items_data):
            # Vary the posting date (random day in the last 30 days)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            posting_date = base_date - timedelta(days=days_ago, hours=hours_ago)
            
            new_item = DBItem(
                title=item_data["title"],
                description=item_data["description"],
                category=item_data["category"],
                status=item_data["status"],
                claimed_by_note=item_data.get("claimed_by_note"),
                date_posted=posting_date
            )
            
            db.add(new_item)
            print(f"Added: {item_data['title']}")
        
        db.commit()
        print(f"\nSuccessfully added {len(items_data)} dummy items to the database!")
        
        # Print summary
        total_items = db.query(DBItem).count()
        available_items = db.query(DBItem).filter(DBItem.status == ItemStatusEnum.AVAILABLE.value).count()
        claimed_items = db.query(DBItem).filter(DBItem.status == ItemStatusEnum.CLAIMED.value).count()
        gone_items = db.query(DBItem).filter(DBItem.status == ItemStatusEnum.GONE.value).count()
        
        print(f"\nDatabase Summary:")
        print(f"Total items: {total_items}")
        print(f"Available: {available_items}")
        print(f"Claimed: {claimed_items}")
        print(f"Gone: {gone_items}")
        
    except Exception as e:
        print(f"Error creating dummy data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating dummy data for UbuntuCycle database...")
    create_dummy_items()