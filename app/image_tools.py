"""Image generation and public Cloud Storage hosting tools for VisualAssist."""

import io
import uuid
from PIL import Image, ImageDraw, ImageFont
from google.cloud import storage

BUCKET_NAME = "visual-assist-assets-qwiklabs-gcp-03-654e96f826b4"
PROJECT_ID = "qwiklabs-gcp-03-654e96f826b4"


def generate_item_visual_aid_card_image(item_name: str, tactile_marker: str, location: str) -> str:
    """Generate a high-contrast visual identification card image for an item,
    uploads it to the public Cloud Storage bucket, and returns its public HTTPS URL.

    Args:
        item_name: Name of the item or medication (e.g. 'Lisinopril 10mg').
        tactile_marker: Tactile/touch identifier (e.g. 'Two red rubber bands').
        location: Storage location (e.g. 'Medicine Cabinet, top shelf').

    Returns:
        Public HTTPS URL string of the uploaded image suitable for embedding in an A2UI Image component.
    """
    width, height = 600, 400
    # Create dark high-contrast background (navy/black)
    img = Image.new("RGB", (width, height), color="#0F172A")
    draw = ImageDraw.Draw(img)

    # Accent top banner (bright amber/yellow for contrast)
    draw.rectangle([(0, 0), (width, 24)], fill="#F59E0B")

    # Outer border
    draw.rectangle([(8, 8), (width - 8, height - 8)], outline="#38BDF8", width=3)

    # Decorative pill/container tactile badge box
    draw.rounded_rectangle([(30, 45), (140, 155)], radius=15, fill="#1E293B", outline="#F43F5E", width=4)
    # Tactile marker graphic indicator inside box
    draw.ellipse([(60, 75), (110, 125)], fill="#F43F5E", outline="#FFFFFF", width=3)

    # Text details
    try:
        font_title = ImageFont.load_default(size=24)
        font_sub = ImageFont.load_default(size=18)
        font_body = ImageFont.load_default(size=16)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Draw titles and descriptions in high-contrast crisp text
    draw.text((160, 55), "VISUAL & TACTILE AID", fill="#38BDF8", font=font_sub)
    draw.text((160, 85), item_name[:32], fill="#FFFFFF", font=font_title)

    draw.line([(30, 180), (width - 30, 180)], fill="#334155", width=2)

    draw.text((35, 205), "TACTILE CUE:", fill="#FBBF24", font=font_sub)
    draw.text((35, 235), tactile_marker[:55], fill="#F8FAFC", font=font_body)

    draw.text((35, 280), "LOCATION:", fill="#34D399", font=font_sub)
    draw.text((35, 310), location[:55], fill="#F8FAFC", font=font_body)

    # Footer indicator
    draw.text((35, 360), "VisualAssist • High-Contrast Daily Living Guide", fill="#94A3B8", font=font_body)

    # Save to buffer as PNG
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Upload to Cloud Storage
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    filename = f"visual_aids/{uuid.uuid4().hex}.png"
    blob = bucket.blob(filename)
    blob.upload_from_file(buffer, content_type="image/png")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url
