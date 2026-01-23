#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General Evolve Agent Runner - Refactored to use BasePESRunner.
"""

import argparse
from typing import Any, Dict, List, Tuple, Type

from agents.general_agent.planner import GeneralPlanAgent
from loongflow.framework.pes import Worker
from loongflow.framework.pes.base_runner import BasePESRunner


class GeneralPESAgent(BasePESRunner):
    """
    General Evolve Agent runner for flexible general-purpose tasks.

    Extends BasePESRunner with:
    - Support for initial code file (--initial-file)
    - Example name parameter (--example-name) for skill loading
    - General-purpose task support
    """

    # def _add_custom_args(self, parser: argparse.ArgumentParser) -> None:
    #     """Add general-agent specific CLI arguments."""
    #     parser.add_argument(
    #         "--task-dir",
    #         type=str,
    #         default=None,
    #         help="Task directory Path",
    #     )
    #
    # def _merge_custom_configs(
    #     self, args: argparse.Namespace, config: Dict[str, Any]
    # ) -> Dict[str, Any]:
    #     """Handle general-agent specific config merging."""
    #     # Add example_name to task description
    #     if args.task_dir:
    #         config["evolve"]["task_dir"] = args.task_dir
    #
    #     return config

    def _get_process_name(self) -> str:
        return "General PES Agent"

    def _get_worker_registrations(
        self,
    ) -> Tuple[
        List[Tuple[str, Type[Worker]]],
        List[Tuple[str, Type[Worker]]],
        List[Tuple[str, Type[Worker]]],
    ]:
        """Register General agent workers."""
        planners = [("general_planner", GeneralPlanAgent)]
        return planners, None, None


if __name__ == "__main__":
    runner = GeneralPESAgent()
    runner.start()
