from dataclasses import dataclass

from typing import Optional, List

from loongflow.framework.pes.context import LLMConfig


@dataclass
class ClaudeAgentConfig:
    """Claude Agent configuration"""

    llm_config: LLMConfig
    system_prompt: Optional[str] = None
    build_in_tools: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    max_turns: Optional[int] = None
    max_rounds: Optional[int] = None
    max_thinking_tokens: Optional[int] = None
    permission_mode: Optional[str] = "acceptEdits"


Details_format = """{
    "reason": "xxxx",
    "assumptions": [
        {
            "assumption": "",
            "evidences": [
                {
                    "evidence_type": "NecessarySign / ContraIndicator / ConfirmingSign",
                    "description": "xxx",
                    "detect_tool": "xxx",
                    "tool_params": {
                    },
                    "weight": "High"
                },
            ]
        }
    ]
}"""

Implementation_format = """{
    "assumption": "xxx",
    "evidences": [
        {
            "evidence_type": "NecessarySign / ContraIndicator / ConfirmingSign",
            "description": "",
            "collected_evidence": ["xxx", "xxx"],
            "result": 1 or 0 or 0.8,
            "weight": "High / Medium / Low"
        }
    ]
}"""