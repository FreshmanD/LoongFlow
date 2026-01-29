# -*- coding: utf-8 -*-
"""
This file define
"""

import pytest

from agents.general_agent.evaluator import GeneralEvaluator
from agents.general_agent.executor import GeneralExecuteAgent
from loongflow.agentsdk.message import Message, MimeType
from loongflow.framework.pes.context import Context, LLMConfig, EvaluatorConfig
from loongflow.framework.pes.executor import Executor
from loongflow.framework.pes.register import register_worker


@pytest.mark.asyncio
async def test_run():
    """test general executor"""
    full_config = {
        "llm_config": LLMConfig(
            model="deepseek-v3.2",
        ),
        "max_turns": 20,
        "max_rounds": 1,
    }
    register_worker("general_executor", "executor", GeneralExecuteAgent)

    evaluator_config = EvaluatorConfig(
        llm_config=LLMConfig(
            model="deepseek-v3.2",
        ),
        timeout=1800,
        agent={
            "max_turns": 10,
        },
    )

    evaluate_code = ""

    evaluator_config.evaluate_code = evaluate_code

    evaluator = GeneralEvaluator(evaluator_config)

    executor = Executor("general_executor", full_config, evaluator, None)

    message = await executor.run(
        context=Context(
            base_path="./output",
            task="""    Traceback (most recent call last):
      File "/Users/daixunan/baidu/agent/LoongFlow/tests/ccsdk/utils.py", line 14, in <module>
        main()
      File "/Users/daixunan/baidu/agent/LoongFlow/tests/ccsdk/utils.py", line 11, in main
        calculate_average([])
      File "/Users/daixunan/baidu/agent/LoongFlow/tests/ccsdk/utils.py", line 5, in calculate_average
        return total / len(numbers)
              ~~~~~~^~~~~~~~~~~~~~
    ZeroDivisionError: division by zero""",
        ),
        message=Message.from_content(
            data={
                "best_plan_file_path": "./output/test/planner/best_plan.md",
                "parent_info_file_path": "./output/test/planner/parent_info.json",
            },
            mime_type=MimeType.APPLICATION_JSON,
        ),
    )

    print(message)
