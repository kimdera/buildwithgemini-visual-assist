"""Video generation and public Cloud Storage hosting tool using gemini-omni-flash-preview."""

import base64
import json
import uuid
import urllib.request
import google.auth
from google.auth.transport.requests import Request
from google.cloud import storage
from google.genai import types
from google.adk.tools import ToolContext

BUCKET_NAME = "visual-assist-assets-qwiklabs-gcp-03-654e96f826b4"
PROJECT_ID = "qwiklabs-gcp-03-654e96f826b4"
LOCATION = "global"
MODEL_ID = "gemini-omni-flash-preview"


async def generate_item_video(
    item_name: str,
    description: str,
    tool_context: ToolContext,
) -> str:
    """Generate a short video for an item or household object using Google's Omni model (gemini-omni-flash-preview)
    in the global region. The video is saved to the Playground's Artifacts panel and uploaded
    to public Cloud Storage, returning its public HTTPS URL.

    Args:
        item_name: Name of the item or medication (e.g. 'Lisinopril 10mg bottle', 'Steel-cut Oats container').
        description: Visual and tactile description to depict (e.g. 'Close-up slow rotation showing bright tactile tape and clear label on a kitchen counter').
        tool_context: ADK ToolContext used to save the video artifact for the Playground.

    Returns:
        Public HTTPS URL string of the uploaded video in Cloud Storage.
    """
    # 1. Obtain auth token for Vertex AI interactions endpoint
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(Request())
    token = credentials.token

    prompt = (
        f"A clear, steady 3-second close-up video of {item_name}. {description}. "
        f"High visibility, clear lighting, slow deliberate motion."
    )

    url = f"https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/interactions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    payload = {
        "model": MODEL_ID,
        "input": [
            {
                "type": "text",
                "text": prompt,
            }
        ],
        "response_format": [
            {
                "type": "video",
                "delivery": "inline",
                "aspect_ratio": "16:9",
                "duration": "3s",
            }
        ],
        "generation_config": {
            "video_config": {
                "task": "text_to_video",
            }
        },
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        resp_data = json.loads(resp.read().decode("utf-8"))

    # Extract video base64 bytes from model_output step
    video_bytes = None
    steps = resp_data.get("steps", [])
    for step in steps:
        if step.get("type") == "model_output":
            for content in step.get("content", []):
                if content.get("type") == "video" and content.get("data"):
                    video_bytes = base64.b64decode(content["data"])
                    break
        if video_bytes:
            break

    if not video_bytes:
        raise RuntimeError(f"No video data returned by {MODEL_ID}. Response: {resp_data}")

    # (1) Save video with tool_context.save_artifact so it appears in Playground's Artifacts panel
    artifact_name = f"{item_name.lower().replace(' ', '_')[:30]}_{uuid.uuid4().hex[:6]}.mp4"
    part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    await tool_context.save_artifact(filename=artifact_name, artifact=part)

    # (2) Upload video bytes directly to public Cloud Storage bucket
    blob_name = f"videos/{uuid.uuid4().hex}_{artifact_name}"
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    # Return public HTTPS URL (https://storage.googleapis.com/<bucket>/<object>)
    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"
    return public_url
