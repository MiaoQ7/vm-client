from app.libs.map import Map

bb = Map()

def get_type():
  return bb.config._args["type"]

def get_name():
  return bb.config._args["name"]

def get_imei():
  return f"{get_type()}-{get_name()}"

def get_machine_id():
  return get_name()
