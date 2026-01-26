from dataclasses import dataclass

from typing import Optional, List

from loongflow.framework.pes.context import LLMConfig

@dataclass
class ClaudeAgentConfig:
    """Planner configuration"""

    llm_config: LLMConfig
    system_prompt: Optional[str] = None
    build_in_tools: Optional[List[str]] = None
    skills: Optional[List[str]] = None
