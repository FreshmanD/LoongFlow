import asyncio
import os

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

os.environ["ANTHROPIC_BASE_URL"] = "https://qianfan.baidubce.com/anthropic"
os.environ["ANTHROPIC_API_KEY"] = (
    "bce-v3/ALTAK-D9BMMcLP9rvJKChqyAK8D/988a0b23bba357d11ab095afd55881eb0fef481f"
)


async def main():
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt="Review tests/ccsdk/utils.py for bugs that would cause crashes. Fix any issues you find.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],  # Tools Claude can use
            permission_mode="acceptEdits",  # Auto-approve file edits
        ),
    ):
        # Print human-readable output
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)  # Claude's reasoning
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")  # Tool being called
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")  # Final result


asyncio.run(main())
