from typing import Any, Dict, Optional

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    file_name: Optional[str]
    file_extension: Optional[str]
    file_base64: Optional[str]
    target_json_example: Optional[str]

    extracted_preview: Optional[str]
    answer: Optional[str]
    meta: Optional[Dict[str, Any]]