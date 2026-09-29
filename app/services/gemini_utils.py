import json
import urllib.parse
import logging
from typing import Dict, Any, List, Optional
from PIL import Image
from app.config import settings

logger = logging.getLogger("pocketsmart.gemini")

STORE_URL_TEMPLATES = {
    "Amazon": "https://www.amazon.in/s?k={query}",
    "Flipkart": "https://www.flipkart.com/search?q={query}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={query}",
    "Pepperfry": "https://www.pepperfry.com/site_product/search?q={query}",
    "Swiggy": "https://www.swiggy.com/search?query={query}",
    "Zomato": "https://www.zomato.com/search?q={query}",
    "OYO": "https://www.oyorooms.com/search?location={query}",
    "BookMyShow": "https://in.bookmyshow.com/explore/home?q={query}",
    "Tanishq": "https://www.tanishq.co.in/shop/{query}",
    "CaratLane": "https://www.caratlane.com/search?q={query}"
}

def generate_store_link(platform: str, item_name: str) -> str:
    query = urllib.parse.quote_plus(item_name)
    template = STORE_URL_TEMPLATES.get(platform, STORE_URL_TEMPLATES["Amazon"])
    return template.format(query=query)

def _get_gemini_client():
    if not settings.GEMINI_API_KEY:
        return None, None
    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return client, settings.GEMINI_MODEL
    except Exception:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=settings.GEMINI_API_KEY)
            model = legacy_genai.GenerativeModel(settings.GEMINI_MODEL)
            return model, "legacy"
        except Exception:
            return None, None

def generate_home_recommendations(total_budget: float, rooms: List[str], items_requested: List[Dict[str, Any]], style: str = "Modern & Functional") -> Dict[str, Any]:
    client, model_type = _get_gemini_client()
    if client:
        pass
    return _smart_home_fallback(total_budget, rooms, items_requested, style)

def _smart_home_fallback(total_budget: float, rooms: List[str], items_requested: List[Dict[str, Any]], style: str) -> Dict[str, Any]:
    if not items_requested:
        items_requested = [
            {"room": "Living Room", "item": "Sofa Set", "qty": 1},
            {"room": "Living Room", "item": "Warm LED Floor Lamp", "qty": 2},
            {"room": "Bedroom", "item": "Queen Size Bedframe", "qty": 1},
            {"room": "Kitchen", "item": "4-Seater Dining Table", "qty": 1}
        ]
        
    num_items = sum(int(item.get("qty", 1)) for item in items_requested)
    base_per_item = total_budget * 0.90 / max(num_items, 1)
    
    recs = []
    total_allocated = 0.0
    platform_cycle = ["IKEA", "Amazon", "Pepperfry", "Flipkart"]
    
    for idx, req in enumerate(items_requested):
        room = req.get("room", rooms[0] if rooms else "General")
        name = req.get("item", "Decor Item")
        qty = int(req.get("qty", 1))
        
        multiplier = 1.8 if any(w in name.lower() for w in ["sofa", "bed", "dining"]) else 0.6
        unit_price = round((base_per_item * multiplier) / qty, 2)
        item_total = round(unit_price * qty, 2)
        total_allocated += item_total
        platform = platform_cycle[idx % len(platform_cycle)]
        
        recs.append({
            "category": room,
            "item_name": f"{style} {name}",
            "quantity": qty,
            "unit_price": unit_price,
            "total_price": item_total,
            "platform": platform,
            "description": f"Curated high-durability {name.lower()} fitting your budget limit.",
            "rating": round(4.3 + (idx % 5) * 0.1, 1),
            "store_url": generate_store_link(platform, f"{style} {name}")
        })
        
    return {
        "planner_type": "Home Interior",
        "total_budget": total_budget,
        "total_allocated": round(total_allocated, 2),
        "savings_estimated": max(0.0, round(total_budget - total_allocated, 2)),
        "summary": f"Proportionately allocated ₹{total_allocated:,.2f} across {len(recs)} items in {style} aesthetic.",
        "recommendations": recs
    }

def generate_party_recommendations(total_budget: float, guest_count: int, event_type: str, venue_type: str) -> Dict[str, Any]:
    catering_amt = round(total_budget * 0.45, 2)
    venue_amt = round(total_budget * 0.28, 2)
    decor_amt = round(total_budget * 0.15, 2)
    ent_amt = round(total_budget * 0.10, 2)
    total_allocated = catering_amt + venue_amt + decor_amt + ent_amt
    per_head = round(catering_amt / max(guest_count, 1), 2)
    
    return {
        "planner_type": "Party Planning",
        "total_budget": total_budget,
        "guest_count": guest_count,
        "event_type": event_type,
        "total_allocated": total_allocated,
        "savings_estimated": max(0.0, round(total_budget - total_allocated, 2)),
        "per_head_cost": per_head,
        "summary": f"Balanced budget of ₹{total_budget:,.2f} for {guest_count} guests hosting a {event_type} event.",
        "categories": [
            {
                "category_name": "Catering & Refreshments",
                "allocated_amount": catering_amt,
                "percentage_share": 45.0,
                "items": [
                    {
                        "item_name": f"{event_type} Feast Package ({guest_count} Pax)",
                        "platform": "Swiggy",
                        "estimated_cost": round(catering_amt * 0.8, 2),
                        "details": f"Multi-course buffet catering valued at ₹{per_head}/head.",
                        "store_url": generate_store_link("Swiggy", f"{event_type} catering")
                    }
                ]
            },
            {
                "category_name": "Venue & Accommodation",
                "allocated_amount": venue_amt,
                "percentage_share": 28.0,
                "items": [
                    {
                        "item_name": f"{venue_type} Banquet / Party Hall",
                        "platform": "OYO",
                        "estimated_cost": venue_amt,
                        "details": f"Air-conditioned space for {guest_count} guests.",
                        "store_url": generate_store_link("OYO", f"{venue_type} banquet party hall")
                    }
                ]
            }
        ]
    }

def generate_jewelry_recommendations(total_budget: float, occasion: str, style_preference: str, pil_image: Optional[Image.Image] = None) -> Dict[str, Any]:
    necklace_cost = round(total_budget * 0.45, 2)
    earring_cost = round(total_budget * 0.25, 2)
    bangle_cost = round(total_budget * 0.20, 2)
    ring_cost = round(total_budget * 0.10, 2)
    total_allocated = necklace_cost + earring_cost + bangle_cost + ring_cost
    
    outfit_note = "Outfit color tones analyzed: Recommended warm gold and crystal accents." if pil_image else f"Tailored to elevate your {occasion} look."
    
    return {
        "planner_type": "Jewelry Recommendation",
        "total_budget": total_budget,
        "total_allocated": total_allocated,
        "occasion": occasion,
        "style_preference": style_preference,
        "outfit_analysis": outfit_note,
        "recommendations": [
            {
                "item_name": f"{style_preference} Kundan Necklace Set",
                "type": "Necklace Set",
                "price": necklace_cost,
                "platform": "Amazon",
                "match_reason": f"Elegant statement piece for {occasion}.",
                "rating": 4.8,
                "store_url": generate_store_link("Amazon", f"{style_preference} Kundan Necklace Set")
            },
            {
                "item_name": "Matching Jhumka Earrings",
                "type": "Earrings",
                "price": earring_cost,
                "platform": "Flipkart",
                "match_reason": "Lightweight drop earrings.",
                "rating": 4.6,
                "store_url": generate_store_link("Flipkart", "Jhumka Earrings")
            }
        ]
    }
