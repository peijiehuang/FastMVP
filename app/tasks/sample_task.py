"""示例定时任务函数。

invokeTarget 引用格式：
  sample_task.no_params
  sample_task.with_params('ry')
  sample_task.with_multi_params('ry', True, 2000)
"""
import logging

logger = logging.getLogger(__name__)


def no_params():
    logger.info("执行示例任务: no_params")
    return "no_params 执行成功"


def with_params(param: str):
    logger.info(f"执行示例任务: with_params({param})")
    return f"with_params 执行成功: {param}"


def with_multi_params(s: str, b: bool, n: int):
    logger.info(f"执行示例任务: with_multi_params({s}, {b}, {n})")
    return f"with_multi_params 执行成功: s={s}, b={b}, n={n}"
