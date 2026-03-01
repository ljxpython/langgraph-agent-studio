from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path

from langchain_core.messages import HumanMessage


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _load_demo_graph():
    graph_file = _PROJECT_ROOT / "graph_src_v2" / "agents" / "no_nested_ainvoke_demo" / "graph.py"
    spec = importlib.util.spec_from_file_location("no_nested_ainvoke_demo_graph", graph_file)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.graph


def test_no_nested_demo_registered_in_langgraph_json() -> None:
    langgraph_file = _PROJECT_ROOT / "graph_src_v2" / "langgraph.json"
    data = json.loads(langgraph_file.read_text(encoding="utf-8"))
    assert "no_nested_ainvoke_demo" in data["graphs"]
    assert "assistant_entrypoint" in data["graphs"]


def test_no_nested_demo_graph_invokes_directly() -> None:
    graph = _load_demo_graph()

    async def _run() -> str:
        result = await graph.ainvoke({"messages": [HumanMessage(content="hello")]}, context={})
        messages = result.get("messages", [])
        assert messages
        return str(messages[-1].content)

    content = asyncio.run(_run())
    assert "[no-nested-demo]" in content
