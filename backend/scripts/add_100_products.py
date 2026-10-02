#!/usr/bin/env python3
"""Add 100 additional products to the catalog."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from decimal import Decimal
from bson import ObjectId
from pymongo import MongoClient
from app.config import settings

# Additional product templates for 100 more products
ADDITIONAL_PRODUCTS = [
    # Peripherals
    ("Ergonomic Vertical Mouse", "peripherals", "49.99", {"dpi": 3200, "sensor": "optical"}),
    ("Trackball Mouse", "peripherals", "69.99", {"dpi": 2400, "sensor": "laser"}),
    ("Gaming Mouse RGB", "peripherals", "79.99", {"dpi": 16000, "sensor": "optical", "rgb": True}),
    ("Compact Mechanical Keyboard", "peripherals", "89.99", {"switch": "red", "layout": "65%"}),
    ("Wireless Numpad", "peripherals", "29.99", {"keys": 21, "connectivity": "bluetooth"}),
    ("Split Ergonomic Keyboard", "peripherals", "159.99", {"switch": "brown", "layout": "split"}),
    ("Macro Keypad", "peripherals", "39.99", {"keys": 15, "programmable": True}),
    ("Mouse Bungee", "peripherals", "14.99", {"material": "silicone"}),
    ("Wrist Rest", "peripherals", "19.99", {"material": "memory foam"}),
    ("Keyboard Cover", "peripherals", "12.99", {"material": "silicone"}),
    ("Desk Mat XL", "peripherals", "34.99", {"material": "stitched cloth", "size": "900x400mm"}),
    ("Cable Management Tray", "peripherals", "24.99", {"material": "steel"}),
    ("Monitor Light Bar", "peripherals", "59.99", {"color_temp": "adjustable"}),
    ("USB Microphone", "peripherals", "89.99", {"pattern": "cardioid", "connectivity": "USB-C"}),
    ("Stream Deck Mini", "peripherals", "79.99", {"keys": 6, "lcd": True}),
    # Audio
    ("Open-Back Headphones", "audio", "249.99", {"impedance": "300ohm", "driver": "dynamic"}),
    ("In-Ear Monitors", "audio", "149.99", {"driver": "balanced armature", "detachable": True}),
    ("Portable DAC/Amp", "audio", "129.99", {"chip": "ESS9281", "output": "4.4mm balanced"}),
    ("Bluetooth Receiver", "audio", "29.99", {"codec": "LDAC", "battery": "12h"}),
    ("Headphone Stand", "audio", "24.99", {"material": "aluminum"}),
    ("Desktop Speakers 2.0", "audio", "119.99", {"power": "15W", "input": "RCA/3.5mm"}),
    ("Subwoofer", "audio", "199.99", {"power": "50W", "size": "8inch"}),
    ("Audio Interface", "audio", "179.99", {"inputs": 2, "outputs": 2, "phantom": True}),
    ("Pop Filter", "audio", "14.99", {"type": "double layer"}),
    ("Shock Mount", "audio", "29.99", {"compatibility": "universal"}),
    ("Acoustic Panels 12pk", "audio", "49.99", {"material": "foam", "thickness": "2inch"}),
    ("Studio Monitor Pair", "audio", "299.99", {"size": "5inch", "biamped": True}),
    ("Headphone Amp", "audio", "89.99", {"output": "6.35mm", "gain": "3-stage"}),
    ("Vinyl Record Player", "audio", "229.99", {"speed": "33/45", "preamp": "built-in"}),
    ("Record Cleaning Kit", "audio", "24.99", {"includes": ["brush", "solution", "cloth"]}),
    # Cables
    ("USB-C to USB-C 100W", "cables", "19.99", {"length": "2m", "data": "USB 3.1"}),
    ("USB-C to USB-A", "cables", "9.99", {"length": "1.5m", "data": "USB 3.0"}),
    ("Thunderbolt 4 Cable", "cables", "59.99", {"length": "0.8m", "speed": "40Gbps"}),
    ("DisplayPort 1.4", "cables", "16.99", {"length": "2m", "hdr": True}),
    ("HDMI 2.1 Cable", "cables", "24.99", {"length": "3m", "bandwidth": "48Gbps"}),
    ("Ethernet Cat6a", "cables", "12.99", {"length": "3m", "shielded": True}),
    ("Coiled Keyboard Cable", "cables", "29.99", {"connector": "USB-C", "color": "custom"}),
    ("Magnetic USB-C Cable", "cables", "14.99", {"tips": ["USB-C", "Lightning", "Micro-USB"]}),
    ("Cable Clips 20pk", "cables", "7.99", {"material": "silicone", "adhesive": "3M"}),
    ("Cable Sleeve 2m", "cables", "8.99", {"material": "PET", "diameter": "10mm"}),
    ("Wireless Charger 3-in-1", "cables", "49.99", {"output": "15W", "devices": 3}),
    ("Power Strip 8-outlet", "cables", "34.99", {"surge": "1200J", "usb": "2x USB-C"}),
    ("Extension Cord 5m", "cables", "18.99", {"gauge": "14AWG", "outlets": 3}),
    ("Travel Power Strip", "cables", "24.99", {"outlets": 3, "usb": "2x USB-A"}),
    ("Cable Ties 100pk", "cables", "6.99", {"material": "velcro", "length": "20cm"}),
    # Office
    ("Standing Desk Converter", "office", "199.99", {"height_range": "6-17in", "width": "32in"}),
    ("Ergonomic Chair", "office", "399.99", {"adjust": ["height", "lumbar", "arms", "tilt"]}),
    ("Foot Rest", "office", "29.99", {"material": "memory foam", "angle": "adjustable"}),
    ("Document Holder", "office", "19.99", {"capacity": "20 sheets", "angle": "adjustable"}),
    ("Desk Shelf", "office", "49.99", {"material": "wood", "size": "60x20cm"}),
    ("Drawer Organizer", "office", "15.99", {"compartments": 8, "material": "bamboo"}),
    ("Pen Holder", "office", "12.99", {"material": "aluminum", "slots": 4}),
    ("Business Card Holder", "office", "18.99", {"capacity": "50", "material": "leather"}),
    ("Desk Clock", "office", "22.99", {"display": "LED", "alarm": True}),
    ("Plant Pot Self-Watering", "office", "24.99", {"material": "ceramic", "reservoir": "200ml"}),
    ("Air Purifier Mini", "office", "79.99", {"filter": "HEPA", "coverage": "10m2"}),
    ("Desk Humidifier", "office", "34.99", {"capacity": "500ml", "mist": "ultrasonic"}),
    ("Blue Light Glasses", "office", "29.99", {"lens": "anti-reflective", "frame": "TR90"}),
    ("Posture Corrector", "office", "24.99", {"size": "adjustable", "material": "breathable"}),
    ("Desk Exercise Bike", "office", "299.99", {"resistance": "8 levels", "display": "LCD"}),
    ("Balance Board", "office", "59.99", {"material": "wood", "angle": "15deg"}),
    ("Under Desk Treadmill", "office", "499.99", {"speed": "1-6kmh", "remote": True}),
    ("Monitor Riser", "office", "34.99", {"height": "10cm", "storage": True}),
    ("Keyboard Tray", "office", "79.99", {"track": "ball-bearing", "width": "60cm"}),
    ("CPU Holder", "office", "29.99", {"mount": "under desk", "adjustable": True}),
    # Additional 35 products to reach 100
    ("Trackpad Gesture Pad", "peripherals", "39.99", {"surface": "glass", "force_touch": True}),
    ("Left-Handed Mouse", "peripherals", "44.99", {"dpi": 3200, "buttons": 6}),
    ("Ambidextrous Mouse", "peripherals", "54.99", {"dpi": 4000, "buttons": 8}),
    ("Silent Click Mouse", "peripherals", "39.99", {"dpi": 2400, "silent": True}),
    ("Heavy Gaming Mouse", "peripherals", "69.99", {"dpi": 12000, "weight": "120g", "weights": True}),
    ("Lightweight Gaming Mouse", "peripherals", "79.99", {"dpi": 26000, "weight": "58g"}),
    ("Macro Mechanical Keyboard", "peripherals", "119.99", {"switch": "silver", "macro_keys": 6}),
    ("Low Profile Keyboard", "peripherals", "99.99", {"switch": "low profile red", "height": "22mm"}),
    ("Ortholinear Keyboard", "peripherals", "139.99", {"layout": "ortho", "keys": 48}),
    ("Mac Keyboard", "peripherals", "129.99", {"layout": "mac", "keys": "scissor"}),
    ("Number Pad Mechanical", "peripherals", "49.99", {"switch": "brown", "keys": 21}),
    ("Media Control Knob", "peripherals", "34.99", {"connectivity": "USB", "display": "OLED"}),
    ("Fingerprint Reader", "peripherals", "29.99", {"standard": "FIDO2", "windows_hello": True}),
    ("Document Scanner", "peripherals", "199.99", {"dpi": "600", "speed": "25ppm"}),
    ("Barcode Scanner", "peripherals", "79.99", {"type": "2D", "connectivity": "USB/Bluetooth"}),
    ("Label Printer", "peripherals", "59.99", {"width": "4inch", "thermal": True}),
    ("ID Card Printer", "peripherals", "899.99", {"resolution": "300dpi", "encoding": "magstripe"}),
    ("Portable Monitor 15.6", "peripherals", "179.99", {"resolution": "1080p", "panel": "IPS", "usb_c": True}),
    ("Portable Monitor 4K", "peripherals", "349.99", {"resolution": "4K", "panel": "OLED", "usb_c": True}),
    ("Drawing Tablet Small", "peripherals", "79.99", {"area": "6x3.7in", "pressure": "4096"}),
    ("Drawing Tablet Medium", "peripherals", "199.99", {"area": "8.5x5.3in", "pressure": "8192"}),
    ("Drawing Tablet Large", "peripherals", "399.99", {"area": "10x6.2in", "pressure": "8192", "screen": True}),
    ("Streaming Light Key", "audio", "149.99", {"lumens": 2800, "temp": "2900-6500K"}),
    ("Streaming Light Fill", "audio", "99.99", {"lumens": 900, "temp": "2900-6500K"}),
    ("Green Screen", "audio", "89.99", {"size": "5x7ft", "material": "polyester"}),
    ("Teleprompter", "audio", "159.99", {"size": "10inch", "app": "included"}),
    ("Capture Card 4K", "audio", "229.99", {"input": "HDMI 2.0", "output": "USB 3.0", "pass_through": "4K60"}),
    ("Capture Card HD", "audio", "129.99", {"input": "HDMI", "output": "USB 3.0", "pass_through": "1080p60"}),
    ("MIDI Controller 25", "audio", "79.99", {"keys": 25, "pads": 8, "knobs": 8}),
    ("MIDI Controller 49", "audio", "149.99", {"keys": 49, "pads": 16, "faders": 9}),
    ("Audio Mixer 4ch", "audio", "89.99", {"channels": 4, "usb": True, "effects": True}),
    ("Audio Mixer 8ch", "audio", "179.99", {"channels": 8, "usb": True, "effects": True}),
    ("In-Ear Wireless", "audio", "199.99", {"anc": True, "codec": "LDAC", "battery": "8h"}),
    ("Over-Ear Wireless", "audio", "299.99", {"anc": True, "codec": "LDAC", "battery": "30h"}),
    ("Bone Conduction", "audio", "129.99", {"waterproof": "IP67", "battery": "8h"}),
    ("Sleep Headphones", "audio", "39.99", {"type": "headband", "bluetooth": "5.2"}),
    ("Kids Headphones", "audio", "29.99", {"volume_limit": "85dB", "wired": True}),
]

# Colors for variants
COLORS = [
    ("graphite", "Graphite"),
    ("silver", "Silver"),
    ("space gray", "Space Gray"),
    ("white", "White"),
    ("midnight blue", "Midnight Blue"),
    ("rose gold", "Rose Gold"),
    ("mint green", "Mint Green"),
    ("coral red", "Coral Red"),
]


def add_products():
    client = MongoClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    products = db["products"]
    
    now = datetime.utcnow()
    
    # Get current count
    existing_count = products.count_documents({})
    print(f"Existing products: {existing_count}")
    
    docs = []
    for i, (title, category, price, extra_attrs) in enumerate(ADDITIONAL_PRODUCTS):
        sku_num = existing_count + i + 1
        sku = f"BM-{sku_num:03}"
        
        # Build attributes
        color_idx = i % len(COLORS)
        color_key, color_label = COLORS[color_idx]
        
        attributes = {
            "brand": "BuyMore",
            "color": color_key,
            "material": "aluminum" if category in ("cables", "office") and i % 3 == 0 else "composite"
        }
        attributes.update(extra_attrs)
        
        # Build variants
        variants = []
        for j, (c_key, c_label) in enumerate(COLORS[:3]):  # 3 variants per product
            var_sku = f"{sku}-{c_key.upper()[:2]}"
            variants.append({
                "sku": var_sku,
                "color": c_key,
                "stock": 30 + (j * 10)
            })
        
        # Tags
        tags = [category, "everyday"]
        if "Wireless" in title or "Bluetooth" in title:
            tags.extend(["wireless", "bluetooth"])
        if "RGB" in title:
            tags.append("rgb")
        if "Gaming" in title:
            tags.append("gaming")
        if "Ergonomic" in title:
            tags.append("ergonomic")
        
        doc = {
            "_id": ObjectId(),
            "sku": sku,
            "title": title,
            "description": f"{title} for a more comfortable, connected everyday setup.",
            "price": float(price),
            "category": category,
            "tags": tags,
            "attributes": attributes,
            "variants": variants,
            "active": True,
            "updated_at": now
        }
        docs.append(doc)
    
    if docs:
        result = products.insert_many(docs)
        print(f"Inserted {len(result.inserted_ids)} new products")
        print(f"Total products now: {products.count_documents({})}")
    else:
        print("No products to insert")


if __name__ == "__main__":
    add_products()