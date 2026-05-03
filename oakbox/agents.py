"""Claude API invocation with a tool-use loop for each pipeline phase."""

from __future__ import annotations

import os
from typing import Any

import anthropic

from . import context as ctx
from .context import WRITE_PHASES
from .tools import COMPLETE_TOOL, READ_TOOLS, WRITE_TOOLS, execute

MODEL = os.environ.get("OAKBOX_MODEL", "claude-sonnet-4-6")
MAX_TURNS = 40  # hard limit on back-and-forth turns per phase


def run_phase(feature: dict, phase: str) -> dict[str, Any]:
    """Invoke the agent for `phase` and return its structured output."""
    client = anthropic.Anthropic()  # uses ANTHROPIC_API_KEY from env

    allow_write = phase in WRITE_PHASES
    tools = (READ_TOOLS + WRITE_TOOLS if allow_write else READ_TOOLS) + [COMPLETE_TOOL]

    system = ctx.system_prompt(phase)
    user_msg = ctx.user_message(feature, phase)

    messages: list[dict] = [{"role": "user", "content": user_msg}]

    for turn in range(MAX_TURNS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=8192,
            system=system,
            tools=tools,
            messages=messages,
        )

        tool_uses = [b for b in response.content if b.type == "tool_use"]

        if not tool_uses:
            # Agent sent text-only response — shouldn't happen if prompt is correct
            raise RuntimeError(
                f"Phase '{phase}' turn {turn}: agent returned no tool calls. "
                "Ensure the system prompt instructs the agent to call complete()."
            )

        # Check for completion first
        complete_calls = [t for t in tool_uses if t.name == "complete"]
        if complete_calls:
            return complete_calls[0].input["output"]

        # Execute all tool calls and collect results
        tool_results = []
        for t in tool_uses:
            result_content = execute(t.name, t.input, allow_write)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": t.id,
                "content": result_content,
            })

        # Append assistant turn + tool results and loop
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    raise RuntimeError(
        f"Phase '{phase}' exceeded {MAX_TURNS} turns without calling complete()."
    )
