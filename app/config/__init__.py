import inspect
from importlib import import_module
from app.libs.map import Map, map_merge
from loguru import logger

__all__ = ["load_config"]

config = None


def load_config(env):
  global config
  if config is not None:
    return config
  config = Map()

  _merge_configs(config, ["default", env])
  return config


def _merge_configs(config, envs):
  for env in envs:
    try:
      module = import_module(f"config.{env}")

      items = {}
      for name, value in inspect.getmembers(module):
        if inspect.ismodule(value):
          continue
        if name.startswith("__"):
          continue
        items[name] = value
      map_merge(config, items)
    except ModuleNotFoundError:
      logger.warning("config module [{}.py] does not exists.", env)
