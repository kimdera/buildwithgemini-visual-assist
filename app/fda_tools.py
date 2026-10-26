"""openFDA lookup tool for VisualAssist."""

import urllib.parse
import urllib.request
import json
from typing import Any, Dict


def lookup_medication_fda_guide(medication_name: str) -> Dict[str, Any]:
    """Look up official FDA drug label information, dosage instructions, and warnings.

    Args:
        medication_name: Name of the prescription or OTC medication (e.g. 'Lisinopril', 'Aspirin').

    Returns:
        Dictionary containing indications, dosage, boxed warnings, and storage directions.
    """
    clean_name = medication_name.strip().split()[0]  # grab brand or generic root name
    encoded_query = urllib.parse.quote(f'openfda.brand_name:"{clean_name}" openfda.generic_name:"{clean_name}"')
    url = f"https://api.fda.gov/drug/label.json?search={encoded_query}&limit=1"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VisualAssist-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        results = data.get("results", [])
        if not results:
            return {"status": "not_found", "message": f"No official FDA label found for '{medication_name}'."}

        doc = results[0]

        def get_field(key: str, default: str = "Not specified") -> str:
            val = doc.get(key)
            if isinstance(val, list) and val:
                return val[0][:500]  # truncate long clinical sections
            elif isinstance(val, str):
                return val[:500]
            return default

        return {
            "status": "success",
            "medication": medication_name,
            "purpose_or_indications": get_field("indications_and_usage", get_field("purpose")),
            "dosage_and_administration": get_field("dosage_and_administration"),
            "warnings_or_precautions": get_field("boxed_warning", get_field("warnings")),
            "storage_and_handling": get_field("storage_and_handling", get_field("how_supplied")),
        }
    except Exception as e:
        return {"status": "error", "message": f"Unable to fetch FDA data for '{medication_name}': {str(e)}"}
