"""Firestore backend tools for VisualAssist."""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Pin project ID explicitly to prevent project number resolution on Agent Runtime
FIRESTORE_PROJECT = "qwiklabs-gcp-03-654e96f826b4"
COLLECTION_NAME = "items"

_db = None


def get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client(project=FIRESTORE_PROJECT)
    return _db


def list_items(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List household items, medications, or pantry goods from the catalog.

    Args:
        category: Optional category filter (e.g., 'Medication', 'Pantry', 'Household Aid').

    Returns:
        List of item dictionaries with location, tactile markers, and dosage/notes.
    """
    db = get_db()
    ref = db.collection(COLLECTION_NAME)
    if category:
        docs = ref.where("category", "==", category).stream()
    else:
        docs = ref.stream()

    items = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        items.append(data)
    return items


def search_item(name_or_keyword: str) -> List[Dict[str, Any]]:
    """Search for an item or medication by name, keyword, or tactile marker description.

    Args:
        name_or_keyword: Keyword to match against item names, locations, or descriptions.

    Returns:
        Matching items with tactile, location, and dosage details.
    """
    db = get_db()
    docs = db.collection(COLLECTION_NAME).stream()
    query = name_or_keyword.lower()
    matches = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        name = str(data.get("name", "")).lower()
        location = str(data.get("location", "")).lower()
        tactile = str(data.get("tactile_marker", "")).lower()
        notes = str(data.get("high_contrast_notes", "")).lower()
        if query in name or query in location or query in tactile or query in notes:
            matches.append(data)
    return matches


def add_or_update_item(
    name: str,
    category: str,
    location: str,
    quantity: int = 1,
    tactile_marker: str = "Unmarked",
    dosage_schedule: str = "N/A",
    high_contrast_notes: str = "Standard packaging",
    warnings: str = "None",
    expiration_date: str = "N/A",
    item_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Add a new item or update an existing item in the household inventory.

    Args:
        name: Name of the item or medication.
        category: Category (e.g. 'Medication', 'Pantry', 'Household Aid').
        location: Clear, specific location description (shelf, bin, room).
        quantity: Current count of items.
        tactile_marker: Tactile cues or physical markers (e.g. rubber band, textured tape, notched lid).
        dosage_schedule: Instructions for taking medication, or 'N/A'.
        high_contrast_notes: High-contrast label details (e.g. bright yellow sticker, large bold letters).
        warnings: Special storage or safety warnings.
        expiration_date: Date in YYYY-MM-DD or 'N/A'.
        item_id: Optional ID. If omitted, generated from name.

    Returns:
        Confirmation dict with updated item details.
    """
    db = get_db()
    if not item_id:
        clean_name = "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")
        clean_cat = "".join(c if c.isalnum() else "-" for c in category.lower()).strip("-")
        item_id = f"{clean_cat}-{clean_name}"

    item_data = {
        "id": item_id,
        "name": name,
        "category": category,
        "location": location,
        "quantity": quantity,
        "tactile_marker": tactile_marker,
        "dosage_schedule": dosage_schedule,
        "high_contrast_notes": high_contrast_notes,
        "warnings": warnings,
        "expiration_date": expiration_date,
    }
    db.collection(COLLECTION_NAME).document(item_id).set(item_data)
    return {"status": "success", "message": f"Saved item '{name}'", "item": item_data}
