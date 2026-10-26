"""Seed script for VisualAssist Firestore backend.

Populates initial items in the 'items' collection with high-contrast,
tactile, and accessibility-focused metadata.
"""

from google.cloud import firestore

FIRESTORE_PROJECT = "qwiklabs-gcp-03-654e96f826b4"
COLLECTION_NAME = "items"


def seed_data():
    db = firestore.Client(project=FIRESTORE_PROJECT)
    print(f"Connecting to Firestore with project '{FIRESTORE_PROJECT}'...")

    sample_items = [
        {
            "id": "med-lisinopril",
            "name": "Lisinopril 10mg",
            "category": "Medication",
            "location": "Bathroom Medicine Cabinet - Shelf 1 (Left)",
            "quantity": 30,
            "tactile_marker": "Single rubber band around bottle, square cap",
            "dosage_schedule": "Once daily with breakfast (8:00 AM)",
            "high_contrast_notes": "Orange bottle with large yellow tactile label",
            "warnings": "Do not skip doses. Monitor blood pressure.",
            "expiration_date": "2027-05-15",
        },
        {
            "id": "med-multivitamin",
            "name": "Daily Multivitamin Gummies",
            "category": "Medication",
            "location": "Kitchen Counter - Carousel Tray",
            "quantity": 60,
            "tactile_marker": "Two textured dots on lid",
            "dosage_schedule": "Two gummies daily in the morning",
            "high_contrast_notes": "Dark blue bottle with white lid",
            "warnings": "Store away from heat.",
            "expiration_date": "2027-08-01",
        },
        {
            "id": "pantry-oatmeal",
            "name": "Rolled Oats (1kg)",
            "category": "Pantry",
            "location": "Pantry - Shelf 2 (Center Bin A)",
            "quantity": 2,
            "tactile_marker": "Blue ridged clip on top flap",
            "dosage_schedule": "N/A",
            "high_contrast_notes": "Large white canister with bold black 'OATS' sticker",
            "warnings": "Gluten-friendly, store dry.",
            "expiration_date": "2027-03-10",
        },
        {
            "id": "pantry-chamomile-tea",
            "name": "Chamomile Herbal Tea (40 bags)",
            "category": "Pantry",
            "location": "Kitchen Tea Drawer (Front Row)",
            "quantity": 1,
            "tactile_marker": "Velvet texture tape on container edge",
            "dosage_schedule": "N/A",
            "high_contrast_notes": "Bright yellow tin with tactile notch",
            "warnings": "Caffeine-free.",
            "expiration_date": "2027-11-20",
        },
        {
            "id": "household-magnifier",
            "name": "High-Power LED Handheld Magnifier",
            "category": "Household Aid",
            "location": "Living Room End Table - Top Drawer",
            "quantity": 1,
            "tactile_marker": "Grooved grip handle with switch toggle",
            "dosage_schedule": "N/A",
            "high_contrast_notes": "Matte black handle with neon green power button",
            "warnings": "Uses 2x AA batteries.",
            "expiration_date": "N/A",
        },
    ]

    for item in sample_items:
        doc_id = item["id"]
        db.collection(COLLECTION_NAME).document(doc_id).set(item)
        print(f"Seeded: {item['name']} (ID: {doc_id})")

    print(f"\nSuccessfully seeded {len(sample_items)} items into collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    seed_data()
