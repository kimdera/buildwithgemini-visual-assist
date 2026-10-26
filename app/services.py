"""Service registration for ADK Memory Bank and other services."""

from google.adk.cli.service_registry import get_service_registry
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService

PROJECT_ID = "qwiklabs-gcp-03-654e96f826b4"
LOCATION = "us-east1"
MEMORY_BANK_ID = "1611539899180122112"


def memory_bank_service_factory(uri: str, **kwargs):
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )


try:
    get_service_registry().register_memory_service("agentengine", memory_bank_service_factory)
except Exception:
    pass
