from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_config
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime

from graph_src_v2.agents.assistant_agent.tools import build_assistant_tools
from graph_src_v2.runtime.context import RuntimeContext
from graph_src_v2.runtime.modeling import apply_model_runtime_params, resolve_model
from graph_src_v2.runtime.options import build_runtime_config, context_to_mapping, merge_trusted_auth_context


_NESTED_CONFIGURABLE_BLOCKLIST = frozenset({"checkpoint_id", "checkpoint_ns", "checkpoint_map"})


def _to_runnable_config(value: Any) -> RunnableConfig:
    return value


def _build_nested_agent_config(config: RunnableConfig) -> RunnableConfig:
    nested: dict[str, Any] = dict(config)
    nested.pop("run_id", None)

    configurable = config.get("configurable")
    if isinstance(configurable, Mapping):
        nested_configurable = dict(configurable)
        for key in _NESTED_CONFIGURABLE_BLOCKLIST:
            nested_configurable.pop(key, None)
        nested["configurable"] = nested_configurable

    return _to_runnable_config(nested)


@tool("submit_high_impact_action", description="Submit a high-impact action request for approval before execution.")
def submit_high_impact_action(action: str, details: str) -> str:
    return f"Approved execution request: action={action}; details={details}"


async def _run_assistant(
    state: MessagesState,
    *,
    runtime: Runtime[RuntimeContext],
) -> MessagesState:
    config: RunnableConfig = get_config()
    runtime_context = merge_trusted_auth_context(config, context_to_mapping(runtime.context))
    options = build_runtime_config(config, runtime_context)

    model = apply_model_runtime_params(resolve_model(options.model_spec), options)
    tools = await build_assistant_tools(options)
    tools.append(submit_high_impact_action)

    middleware = [
        HumanInTheLoopMiddleware(
            interrupt_on={
                "submit_high_impact_action": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                    "description": "High-impact action requires human review.",
                }
            },
            description_prefix="Tool execution pending approval",
        )
    ]

    agent = create_agent(
        model=model,
        tools=tools,
        middleware=middleware,
        checkpointer=InMemorySaver(),
        system_prompt=options.system_prompt,
        name="assistant_entrypoint_light_factory",
    )

    result = await agent.ainvoke(
        {"messages": state.get("messages", [])},
        config=_build_nested_agent_config(config),
    )
    return {"messages": result.get("messages", [])}


def make_graph(config: RunnableConfig) -> Any:
    del config
    builder = StateGraph(MessagesState, context_schema=RuntimeContext)
    builder.add_node("run_assistant", _run_assistant)
    builder.add_edge(START, "run_assistant")
    builder.add_edge("run_assistant", END)
    return builder.compile(name="assistant_entrypoint_light_factory")
