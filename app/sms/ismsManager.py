import time
import re
from app.libs import ihttp
from loguru import logger
from . import isms
from . import russia_activate_client
from . import baihe168_client
from . import lemon_client
from . import simCode
from . import idweb
from . import five_sim
from . import gnj2
from . import mimi
from . import rsim
from . import inewbit
from . import ppz
from . import chothue
from . import bazhuayu
from . import bazhuayu_random_area
from .sms_code import SMSCodeClient
from .lsj import LSJClient
from .firefox import FirefoxClient, FirefoxClient2
from .WOOD import WOODClient
from .douya import DouYaClient
from .snails_random import SnailsRandom, SnailsRandom2
from .sms_platform import SmsPlatform

def getClient(params, vpsID, serverPath, smsUrl) -> isms.ISMS:
    switch = {
        "firefox2": lambda: FirefoxClient2(params, vpsID, serverPath),
        "douya": lambda: DouYaClient(params, vpsID, serverPath),
        "WOOD": lambda: WOODClient(params, vpsID, serverPath),
        "baihe168": lambda: baihe168_client.Baihe168Client(params, vpsID, serverPath),
        "lemon": lambda: lemon_client.Client(params, vpsID, serverPath),
        "simCode": lambda: simCode.SimCode(params, vpsID, serverPath),
        "idweb": lambda: idweb.IdWebClient(params, vpsID, serverPath),
        "5sim": lambda: five_sim.FiveSimClient(params, vpsID, serverPath),
        "gnj2": lambda: gnj2.Gnj2Client(params, vpsID, serverPath),
        "mimi": lambda: mimi.MimiClient(params, vpsID, serverPath),
        "rsim": lambda: rsim.RSimClient(params, vpsID, serverPath),
        "inewbit": lambda: inewbit.InewbitClient(params, vpsID, serverPath),
        "ppz": lambda: ppz.PPZClient(params, vpsID, serverPath),
        "chothue": lambda: chothue.Chothue(params, vpsID, serverPath),
        "bazhuayu-random-area": lambda: bazhuayu_random_area.BaZhuoYuRandomAreaClient(params, vpsID, serverPath),
        "snails_random": lambda: SnailsRandom(params, vpsID, serverPath),
        "snails_random2": lambda: SnailsRandom2(params, vpsID, serverPath),
        # "firefox": lambda: SmsPlatform(params, vpsID, serverPath),
        # "bazhuayu": lambda: SmsPlatform(params, vpsID, serverPath),
        # "sms-activate": lambda: SmsPlatform(params, vpsID, serverPath),
        # "sms-code": lambda: SMSCodeClient(params, vpsID, serverPath),
        # "lsj": lambda: LSJClient(params, vpsID, serverPath),
        "sms-platform": lambda: SmsPlatform(params, vpsID, serverPath, smsUrl),
    }
    phonePlatformCode = params["platformCode"]
    if switch.get(phonePlatformCode) is not None:
      client = switch[phonePlatformCode]()
    else:
      client = switch['sms-platform']()
    try:
      if client.login():
        return client
      else:
        raise Exception("账户没有余额")
    except Exception as e:
      raise Exception(e)
