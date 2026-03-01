from __future__ import annotations

from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import FakeListChatModel

from graph_src_v2.runtime.context import RuntimeContext

_model = FakeListChatModel(responses=["[no-nested-demo] assistant replied."] * 100)

graph = create_agent(
    model=_model,
    tools=[],
    middleware=[],
    system_prompt="You are a demo assistant for no-nested-ainvoke architecture.",
    context_schema=RuntimeContext,
    name="assistant_no_nested_demo",
)
