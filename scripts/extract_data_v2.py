import json
import re
import uuid
from datetime import datetime
from pypdf import PdfReader

def clean_text(text):
    if not text:
        return None
    return text.strip().replace('\n', ' ')

def extract_pincode(address):
    if not address:
        return None
    match = re.search(r'\b\d{6}\b', address)
    return match.group(0) if match else None

def extract_state_city(address):
    if not address:
        return None, None
    parts = address.split(',')
    if len(parts) >= 2:
        state = parts[-1].strip()
        state = re.sub(r'\d+', '', state).strip()
        city_part = parts[-2].strip()
        city = re.sub(r'\d+', '', city_part).strip().replace('-', '')
        return city, state
    return None, None

def parse_museums(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages[10:]:
        full_text += page.extract_text() + "\n"

    full_text = full_text.replace("Name :", "Name:").replace("Address :", "Address:")

    museum_blocks = []

    chunks = re.split(r'(?=\bName:)', full_text)
    
    parsed_museums = []
    
    for chunk in chunks:
        if "Name:" not in chunk:
            continue
            
        try:
            name_match = re.search(r'Name:(.*?)(?=\n|Address:|Telephone:|Description:|Collection:|$)', chunk, re.DOTALL)
            address_match = re.search(r'Address:(.*?)(?=\n|Telephone:|Telegraph:|Email:|Website:|Description:|Collection:|$)', chunk, re.DOTALL)

            if not name_match:
                continue
                
            name = clean_text(name_match.group(1))
            if not name or len(name) < 3:
                continue

            address = clean_text(address_match.group(1)) if address_match else None

            desc_match = re.search(r'(Description|History|Collection):(.*?)(?=\n|Name:|Facilities:|Opening|$)', chunk, re.DOTALL | re.IGNORECASE)
            description = clean_text(desc_match.group(2)) if desc_match else f"A museum named {name}."

            website_match = re.search(r'(Website|Web):(.*?)(?=\n|\s+|$)', chunk, re.IGNORECASE)
            website = clean_text(website_match.group(2)) if website_match else None

            phone_match = re.search(r'(Telephone|Tel|Ph):(.*?)(?=\n|Email:|Fax:|Website:|$)', chunk, re.IGNORECASE)
            phone = clean_text(phone_match.group(2)) if phone_match else None

            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', chunk)
            email = email_match.group(0) if email_match else None

            time_match = re.search(r'(Opening|Hours|Time):(.*?)(?=\n|Closed:|Entry:|Name:|$)', chunk, re.IGNORECASE)
            timings = clean_text(time_match.group(2)) if time_match else None

            closed_match = re.search(r'(Closed|Holiday):(.*?)(?=\n|Entry:|Name:|$)', chunk, re.IGNORECASE)
            closed_days = clean_text(closed_match.group(2)) if closed_match else None

            m_type = "General"
            lower_name = name.lower()
            if "science" in lower_name: m_type = "Science"
            elif "art" in lower_name or "gallery" in lower_name: m_type = "Art"
            elif "archaeol" in lower_name: m_type = "Archaeological"
            elif "rail" in lower_name: m_type = "Transport"
            elif "war" in lower_name: m_type = "History"

            pincode = extract_pincode(address)
            city, state = extract_state_city(address)

            museum_obj = {
                "museum_id": str(uuid.uuid4()),
                "museum_name": name,
                "museum_type": m_type,
                "established_year": None,
                "description": description,
                
                "address": address,
                "city": city,
                "state": state,
                "country": "India",
                "pincode": pincode,
                "latitude": None,
                "longitude": None,

                "opening_time": timings,
                "closing_time": None,
                "weekly_off_days": closed_days,
                "entry_fee": None,
                "ticket_currency": "INR",
                "average_visit_duration_minutes": None,

                "max_daily_capacity": None,
                "wheelchair_accessible": False,
                "parking_available": False,
                "guided_tours_available": False,
                "audio_guide_available": False,

                "contact_phone": phone,
                "contact_email": email,
                "official_website": website,
                "google_maps_link": None,

                "cover_image": None,
                "gallery_images": [],
                "video_url": None,

                "average_rating": None,
                "total_reviews": 0,
                "annual_visitors": None,
                "popularity_score": 0,

                "student_discount": None,
                "senior_citizen_discount": None,
                "free_entry_days": None,
                "special_exhibition_fee": None,

                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            parsed_museums.append(museum_obj)
            
        except Exception as e:
            continue

    return parsed_museums

if __name__ == "__main__":
    print("Extracting data...")
    data = parse_museums("Directory_of_Indian_Museums_080620231.pdf")
    with open("museum_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"Extraction complete. Found {len(data)} museums.")
