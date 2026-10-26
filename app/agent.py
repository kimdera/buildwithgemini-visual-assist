# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

try:
    from a2ui.schema.manager import A2uiSchemaManager
    from a2ui.basic_catalog.provider import BasicCatalog
except ImportError:
    A2uiSchemaManager = None
    BasicCatalog = None

from app.instruction import INSTRUCTION
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.inventory_tools import list_items, search_item, add_or_update_item
from app.fda_tools import lookup_medication_fda_guide
from app.nutrition_tools import lookup_food_nutrition_and_ingredients
from app.image_tools import generate_item_visual_aid_card_image
from app.video_tools import generate_item_video
from app.a2ui_utils import a2ui_callback


MODEL = "gemini-3.8-flash"
PROJECT_ID = "qwiklabs-gcp-03-654e96f826b4"
LOCATION = "us-east1"
MEMORY_BANK_ID = "1611539899180122112"
SANDBOX_RESOURCE_NAME = (
    "projects/808375856048/locations/us-east1/reasoningEngines/1611539899180122112/sandboxEnvironments/5351494616199725056"
)


def get_current_time(timezone: str = "America/Los_Angeles") -> str:
    """Get the current time and date to help with medication and daily schedules.

    Args:
        timezone: Timezone identifier (default 'America/Los_Angeles').

    Returns:
        Formatted current date and time string.
    """
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        tz = ZoneInfo("America/Los_Angeles")
    now = datetime.datetime.now(tz)
    return f"Current date and time ({timezone}): {now.strftime('%A, %B %d, %Y at %I:%M %p %Z')}"


# Memory Bank generation callback: extracts and saves durable facts after each turn
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


# Deployed / App Memory Bank service builder
def get_memory_service():
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )


code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=SANDBOX_RESOURCE_NAME,
)

if A2uiSchemaManager is not None and BasicCatalog is not None:
    schema_manager = A2uiSchemaManager(
        version="0.8",
        catalogs=[BasicCatalog.get_config("0.8")],
    )

    instruction = schema_manager.generate_system_prompt(
        role_description=(
            "You are VisualAssist, an empathetic, highly organized AI assistant designed to "
            "support low-vision and visually impaired individuals with daily living, home organization, "
            "and medication tracking."
        ),
        workflow_description=(
            "1. Long-Term Memory & Allergy Safety: You prioritize remembering all user allergies "
            "(medication allergies, food allergies, ingredient sensitivities) and stated preferences across conversations. "
            "Always respect and cross-check these allergies when discussing food, medications, or pantry goods.\n"
            "2. Inventory & Medication Catalog: You can browse items (list_items), look up specific items by name/tactile cues "
            "(search_item), and add or update items (add_or_update_item).\n"
            "3. Orientation & Sensory Guidance: Whenever describing an item's location, always clearly describe its physical "
            "location, tactile markers (e.g. textured rubber bands, braille/ridged stickers), and high-contrast visual markings.\n"
            "4. Medication Safety: Provide clear dosage schedules and safety warnings when asked about medications.\n"
            "5. Calculations & Data Processing: When you need to do complex calculations (e.g. days of medication remaining, "
            "restock dates, unit conversions), use your Python code sandbox to compute the answer safely.\n"
            "Analyze the request and return structured UI when appropriate."
        ),
        ui_description=(
            "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
            "Never nest a Card inside a Card. "
            "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
            "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
            "nothing in adk web). "
            "You may include one Image component, but only when you have a public https "
            "URL for the image (for example the URL an image tool returns after uploading "
            "to a public bucket). Set the Image url to that exact https link, for example "
            '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
            "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
            "not have a public URL, add a short Text line noting the image instead. "
            "No markdown in text; use the usageHint property (\'h1\', \'h2\', \'body\') for "
            "headings and emphasis. "
            "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
            "<a2a_datapart_json> tags or \'kind\'/\'data\'/\'metadata\' objects."
        ),
        include_schema=True,
        include_examples=True,
    )
else:
    instruction = INSTRUCTION

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        list_items,
        search_item,
        add_or_update_item,
        get_current_time,
        lookup_medication_fda_guide,
        lookup_food_nutrition_and_ingredients,
        generate_item_visual_aid_card_image,
        generate_item_video,
    ],
    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
    code_executor=code_executor,
)

app = App(
    root_agent=root_agent,
    name="app",
)
