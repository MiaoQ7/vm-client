import os
import sys
import click
from loguru import logger

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_name = os.path.basename(os.path.normpath(project_path))
sys.path.insert(0, project_path)


def init_logger(**kwargs):
  log_name = f'{kwargs["name"]}'
  log_dir = os.path.join(project_path, "logs")
  log_file = os.path.join(log_dir, f"{log_name}.log")
  error_log_file = os.path.join(log_dir, f"error-{log_name}.log")

  fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
  logger.remove(handler_id=None)
  logger.add(sys.stdout, level="DEBUG", format=fmt)
  logger.add(log_file, level="DEBUG", format=fmt, rotation="100 MB", retention="14 days", compression="zip", encoding="utf8")
  logger.add(error_log_file, level="ERROR", format=fmt, rotation="100 MB", retention="14 days", compression="zip", encoding="utf8")


@click.command()
@click.option("--env", default="dev", type=str, help="env")
@click.option("--type", type=str, help="app type")
@click.option("--name", type=str, help="app name")
@logger.catch
def main(**kwargs):
  from app.utils.trace_utils import start_trace
  from app.config import load_config
  from app.state import loop

  if kwargs["type"] is None or kwargs["name"] is None:
    raise Exception("app type or name can not be null")

  init_logger(**kwargs)

  config = load_config(kwargs["env"])
  config._args = kwargs
  config._project_path = project_path
  config._project_name = project_name
  loop.bb.config = config
  logger.info("load config: {}", config)

  loop.start()

if __name__ == "__main__":
  main()
