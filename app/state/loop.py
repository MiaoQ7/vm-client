import os
import re
import json
import time
from . import tt
from .fs import LocalStorage
from importlib import import_module
from loguru import logger

__all__ = ["tt", "bb", "fs", "start"]

_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_project_path = os.path.dirname(_parent_dir)

bb = tt.bb
fs = LocalStorage(os.path.join(_project_path, "vfs"))

_chains = {}
_taskOutRecord = {}

def _init_chain():
  chain_dir = os.path.join(_parent_dir, "task_chain")
  for fname in os.listdir(chain_dir):
    fpath = os.path.join(chain_dir, fname)
    if os.path.isfile(fpath) and fpath.endswith(".json"):
      chain_name = os.path.splitext(fname)[0]
      with open(fpath, "r") as f:
        _chains[chain_name] = json.load(f)
        logger.info("load chain [{}] from {}", chain_name, fpath)


def _parse_state_result(stateResult, chain):
  next = stateResult.split(":")
  if len(next) == 1:
    state = next[0]
    delay = 0
  elif len(next) == 2:
    if re.match(r"^[\d\.]+$", next[1]) is not None:
      state, delay = next[0], float(next[1])
    else:
      chain, state = next
      delay = 0
  elif len(next) == 3:
    chain, state, delay = next[0], next[1], float(next[2])
  return [chain, state, delay] 


def start(chain="core", state="start"):
  delay = 0
  count = 0
  pre = ""

  _init_chain()

  while(True):
    time.sleep(delay)

    stateUnit = _chains[chain][state]
    if "_out" in stateUnit and count >= stateUnit["_out"][0]:
      chain, state, delay = _parse_state_result(stateUnit["_out"][1], chain)
      logger.info("  count out {}:{} - {}", chain, state, count)
      count = 0
      continue
    
    if "_taskOut" in stateUnit:
      taskKey = f"{chain}:{state}"
      _taskOutRecord[taskKey] = _taskOutRecord.get(taskKey, 0) + 1
      if _taskOutRecord[taskKey] > stateUnit["_taskOut"][0]:
        chain, state, delay = _parse_state_result(stateUnit["_taskOut"][1], chain)
        logger.info("  task out {}:{} - {}", chain, state, count)
        del _taskOutRecord[taskKey]
        continue

    pre = f"{chain}:{state}"
    logger.info("[state] enter {}:{} - {}", chain, state, count + 1)

    if "_alias" in stateUnit:
      alias = stateUnit["_alias"].split(":")
      if len(alias) == 1:
        state = alias[0]
      elif len(alias) == 2:
        chain, state = alias
      logger.info(f"      alias {chain}:{state}")
    
    result = "_error"
    try:
      result = getattr(import_module(f"task.{chain}"), state)()
    except Exception as e:
      logger.exception("{}:{} {}", chain, state, e)
      if result in stateUnit:
        bb._error = e
      else:
        raise e

    if stateUnit[result] == "":
      logger.info(f"loop break. {chain}:{state}")
      break
      
    next = _parse_state_result(stateUnit[result], chain)
    count = count + 1 if pre == f"{next[0]}:{next[1]}" else 0
    chain, state, delay = next

