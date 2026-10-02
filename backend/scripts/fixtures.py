from datetime import timedelta
from decimal import Decimal
from bson import ObjectId

USERS = ["John Doe", "Jane Smith", "Wendy Wireless", "Alex Rivera", "Sam Patel", "Casey Nguyen", "Morgan Lee", "Riley Brooks"]
CATALOG = [
    ("Wireless Mouse", "peripherals", "50.16"),
    ("Mechanical Keyboard", "peripherals", "100.34"),
    ("Wireless Keyboard", "peripherals", "65.00"),
    ("Precision Mouse Pad", "peripherals", "12.00"),
    ("Studio Webcam", "peripherals", "129.00"),
    ("Wireless Trackpad", "peripherals", "89.00"),
    ("Wireless Earbuds", "audio", "79.99"),
    ("Noise Cancelling Headphones", "audio", "199.00"),
    ("Wireless Speaker", "audio", "59.00"),
    ("USB Studio Microphone", "audio", "119.00"),
    ("Wired Earphones", "audio", "18.00"),
    ("Wireless Headset", "audio", "95.00"),
    ("USB-C Hub 7-in-1", "cables", "45.00"),
    ("Braided USB-C Cable", "cables", "9.00"),
    ("HDMI Cable", "cables", "14.00"),
    ("Thunderbolt Dock", "cables", "159.00"),
    ("Ethernet Cable", "cables", "8.00"),
    ("Travel Adapter", "cables", "29.00"),
    ("Desk Lamp LED", "office", "32.50"),
    ("Aluminum Laptop Stand", "office", "49.00"),
    ("Desk Organizer", "office", "16.00"),
    ("Monitor Arm", "office", "109.00"),
    ("Wireless Charging Pad", "office", "39.00"),
    ("Felt Desk Mat", "office", "22.00"),
]


def catalog_documents(now):
    docs = []
    for i, (title, category, price) in enumerate(CATALOG):
        sku = f"BM-{i+1:03}"
        attributes = {"brand": "BuyMore", "color": "graphite", "material": "aluminum" if i in (12, 15, 19, 21) else "composite"}
        if i == 0:
            attributes["dpi"] = 1600
        if i == 12:
            attributes["ports"] = ["USB-C", "USB-A", "HDMI", "SD", "microSD"]
        docs.append({"_id": ObjectId(f"{i+1:024x}"), "sku": sku, "title": title,
                     "description": f"{title} for a more comfortable, connected everyday setup.",
                     "price": float(price), "category": category,
                     "tags": [category, "everyday"] + (["wireless", "bluetooth"] if "Wireless" in title else []),
                     "attributes": attributes,
                     "variants": [{"sku": sku + "-GR", "color": "graphite", "stock": 40}, {"sku": sku + "-WH", "color": "white", "stock": 25}],
                     "active": True, "updated_at": now})
    docs.append({**docs[3], "_id": ObjectId(f"{25:024x}"), "sku": "BM-025", "title": "Archive Mouse Pad", "active": False})
    return docs


def order_fixtures(now):
    for i in range(40):
        # First eight guarantee cheap orders; next twelve establish search fixtures.
        indexes = [13, 16] if i < 8 else ([0, 1, 3] if i < 12 else ([0, 6, 14] if i < 20 else [1, 7, 18, 23]))
        if i == 0:
            indexes = [13]
        user_id = i % 8 + 1
        if user_id == 3 and i >= 8:
            indexes = [0, 6, 14]
        age = i if i < 8 else (65 + i % 20 if i < 16 else 8 + i * 2 % 50)
        if user_id in (7, 8) and i < 24:
            age = 65 + i % 20
        status = 'PENDING' if user_id == 6 else ('SHIPPED' if user_id == 7 else ['PENDING', 'PROCESSING', 'SHIPPED'][i % 3])
        items = [{"product_id": f"{j+1:024x}", "title": CATALOG[j][0], "quantity": 1,
                  "unit_price": Decimal(CATALOG[j][2])} for j in indexes]
        yield {"id": i+1, "user_id": user_id, "status": status,
               "order_date": now - timedelta(days=age), "updated_at": now - timedelta(days=age), "version": 1,
               "total_amount": sum(x["unit_price"] * x["quantity"] for x in items), "items": items}
