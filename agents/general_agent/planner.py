#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file provides general planner implementation based on Claude Code Agent
"""

import json
import os
from typing import Any

from agents.general_agent.common import ClaudeAgentConfig
from agents.general_agent.utils import build_custom_tools_from_function_tools
from loongflow.agentsdk.logger import get_logger
from loongflow.agentsdk.message import Message, MimeType
from loongflow.framework.claude_code import GENERAL_PLANNER_USER, GENERAL_PLANNER_SYSTEM
from loongflow.framework.pes.context import Context, Workspace
from loongflow.framework.pes.database import EvolveDatabase
from loongflow.framework.pes.register import Worker
from loongflow.framework.claude_code.claude_code_agent import ClaudeCodeAgent
from loongflow.framework.pes.database.database_tool import (
    GetBestSolutionsTool,
    GetChildsByParentTool,
    GetMemoryStatusTool,
    GetParentsByChildIdTool,
    GetSolutionsTool,
)

logger = get_logger(__name__)

class GeneralPlanAgent(Worker):
    """Plan Agent Class"""

    def __init__(self, config: Any, db: EvolveDatabase):
        super().__init__()
        self.config = (
            config
            if isinstance(config, ClaudeAgentConfig)
            else ClaudeAgentConfig(**config)
        )

        if self.config.llm_config is None:
            raise ValueError(
                "Planner: No LLMConfig found in config, please check your config."
            )

        self.database = db

        self.custom_tools = [
            GetMemoryStatusTool(self.database.memory_status),
            GetSolutionsTool(self.database.get_solutions),
            GetBestSolutionsTool(self.database.get_best_solutions),
            GetParentsByChildIdTool(self.database.get_parents_by_child_id),
            GetChildsByParentTool(self.database.get_childs_by_parent_id),
        ]

        logger.info("ClaudePlannerWorker: Initialized successfully")

    async def run(self, context: Context, message: Message) -> Message:
        """Execute planning phase."""
        memory_status = self.database.memory_status()
        logger.info(
            f"Trace ID: {context.trace_id}: Planner: Starting iteration {context.current_iteration}, Current Memory Status: {memory_status}"
        )

        # Create agent with context-specific work_dir
        work_dir = str(Workspace.get_planner_path(context, True))
        # Ensure work_dir is absolute path
        if not os.path.isabs(work_dir):
            work_dir = os.path.abspath(work_dir)
        logger.debug(
            f"Trace ID: {context.trace_id}: Planner: Workspace is : {work_dir} (absolute path)"
        )

        # Load skills if specified
        if self.config.skills:
            from .utils import load_skills

            try:
                load_skills(
                    skill_names=self.config.skills,
                    work_dir=work_dir,
                )
                logger.info(
                    f"Trace ID: {context.trace_id}: Loaded skills: {self.config.skills}"
                )
            except Exception as e:
                logger.error(
                    f"Trace ID: {context.trace_id}: Failed to load skills: {str(e)}"
                )
                raise

        # Build database tools for the agent
        database_tools = build_custom_tools_from_function_tools(self.custom_tools)

        agent = ClaudeCodeAgent(
            model=self.config.llm_config.model,
            api_key=self.config.llm_config.api_key,
            url=self.config.llm_config.url,
            work_dir=work_dir,
            tool_list=self.config.build_in_tools,
            custom_tools=database_tools,
            system_prompt=self.config.system_prompt or GENERAL_PLANNER_SYSTEM,
            permission_mode=self.config.llm_config.claude_agent_options.get("permission_mode"),
            setting_sources=["project"],
        )

        # Prepare initial parent info
        init_parent = {
            "solution": context.init_solution,
            "score": context.init_score or 0.0,
            "evaluation": context.init_evaluation,
            "summary": "This is the initial solution, it has no parents. Start evolution from here.",
        }

        # Sample parent from database
        parent = self.database.sample_solution(context.island_id)
        parent_dict = parent if parent else init_parent

        # Save parent info using Workspace
        parent_json = json.dumps(parent_dict, indent=4)
        Workspace.write_planner_parent_info(context, parent_json)
        parent_info_path = Workspace.get_planner_parent_info_path(context)
        logger.debug(
            f"Trace ID: {context.trace_id}: Planner: Write planner parent info to {parent_info_path}"
        )

        # Get the expected plan path
        # Use absolute path to avoid any relative path confusion
        best_plan_full_path = str(Workspace.get_planner_best_plan_path(context))
        # Pass absolute path to Claude - Claude agent will handle it correctly regardless of current working directory
        best_plan_path_for_claude = best_plan_full_path  # Already the correct absolute path since Workspace returns absolute paths

        user_prompt = GENERAL_PLANNER_USER.format(
            task_info=context.task,
            parent_solution=parent_json,
            workspace=f"{work_dir} (absolute path)",
            island_num=self.database.config.num_islands,
            parent_island=parent.get("island_id") if parent else 0,
            best_plan_path=f"{best_plan_path_for_claude} (absolute path)",
        )

        # Execute planning - Claude should use Write tool to save plan to best_plan_path
        result = await agent.run(user_prompt)

        # Check if Claude wrote the plan file (primary path)
        if os.path.exists(best_plan_full_path):
            logger.info(
                f"Trace ID: {context.trace_id}: Planner: Plan generated successfully at {best_plan_full_path}"
            )
        else:
            # Fallback: extract plan from Claude's response and save it manually
            logger.warning(
                f"Trace ID: {context.trace_id}: Planner: Plan file not found at {best_plan_full_path}, "
                "extracting from response as fallback"
            )
            # Extract the plan content from Claude's response
            if result.content and len(result.content) > 0:
                plan_content = result.content[0].data
            else:
                plan_content = str(result.metadata.get("response", "No plan generated"))

            # Save the extracted plan
            Workspace.write_planner_best_plan(context, plan_content)
            logger.info(
                f"Trace ID: {context.trace_id}: Planner: Plan extracted from response and saved to {best_plan_full_path}"
            )

        # Save metadata to JSON file
        meta_content = {
            "trace_id": context.trace_id,
            "status": result.metadata.get("status"),
            "tools_used": result.metadata.get("tools_used", []),
            "input_tokens": result.metadata.get("input_tokens"),
            "output_tokens": result.metadata.get("output_tokens"),
            "duration_ms": result.metadata.get("duration_ms"),
        }

        # Save metadata to meta.json in planner directory
        meta_file_path = os.path.join(work_dir, "meta.json")
        with open(meta_file_path, "w", encoding="utf-8") as f:
            json.dump(meta_content, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Trace ID: {context.trace_id}: Planner: Metadata saved to {meta_file_path}"
        )

        return Message.from_text(
            data={
                "parent_info_file_path": parent_info_path,
                "best_plan_file_path": best_plan_full_path,
                "total_prompt_tokens": result.metadata.get("input_tokens"),
                "total_completion_tokens": result.metadata.get("output_tokens"),
            },
            mime_type=MimeType.APPLICATION_JSON,
        )
