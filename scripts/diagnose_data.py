import json
import csv
import os
import sys

def diagnose():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    csv_path = os.path.join(base_dir, 'final_museums.csv')
    json_path = os.path.join(base_dir, 'museum_data.json')
    
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    
    csv_names = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Name'):
                csv_names.add(row['Name'].strip())
                
    print(f"Unique CSV Names: {len(csv_names)}")
    print("Sample CSV Names:", list(csv_names)[:5])
    
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        
    json_names = set()
    for m in json_data:
        if m.get('museum_name'):
            json_names.add(m['museum_name'].strip())
            
    print(f"Unique JSON Names: {len(json_names)}")
    print("Sample JSON Names:", list(json_names)[:5])
    
    # Check Intersection
    # Normalize for checking
    norm_csv = {n.lower().strip() for n in csv_names}
    norm_json = {n.lower().strip() for n in json_names}
    
    intersection = norm_csv.intersection(norm_json)
    print(f"Exact Matches (insensitive): {len(intersection)}")
    
    print("\n--- NON-MATCHING EXAMPLES (JSON names not in CSV) ---")
    count = 0
    for name in json_names:
        if name.lower().strip() not in norm_csv:
            print(f"JSON: '{name}'")
            count += 1
            if count > 10: break

if __name__ == "__main__":
    diagnose()
