import tracemalloc
import threading
import time
from loguru import logger


def start_trace():
  tracemalloc.start()

  t = threading.Thread(target=_trace)
  t.start()
  logger.info("start trace")

def _trace():
  while True:
    time.sleep(10)

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    logger.info("=======================[ Top 10 ]=======================")
    for stat in top_stats[:10]:
      logger.info(stat)


if __name__ == "__main__":
  start_trace()