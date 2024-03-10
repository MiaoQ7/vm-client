import os
import json
import tempfile
from loguru import logger

class LocalStorage(object):
  def __init__(self, root=tempfile.gettempdir()):
    self.root = root
    if not os.path.exists(root):
      os.makedirs(root)
    
  def get_full_path(self, path):
    return os.path.join(self.root, path)

  def exists(self, path):
    return os.path.exists(self.get_full_path(path))

  def delete_dir(self, full_path):
    if os.path.exists(full_path):
      files = os.listdir(full_path)
      for file in files:
        filepath = os.path.join(full_path, file)
        if os.path.isdir(filepath):
          self.delete_dir(filepath)
        else:
          os.remove(filepath)
      os.rmdir(full_path)
    
  def delete(self, path):
    if path == None or path == "" or path == "/":
      return

    full_path = self.get_full_path(path)
    if not os.path.exists(full_path):
      return

    if os.path.isfile(full_path):
      os.remove(full_path)
    elif os.path.isdir(full_path):
      self.delete_dir(full_path)
    
  def read(self, path, mode="r"):
    full_path = self.get_full_path(path)
    if not os.path.exists(full_path):
      logger.warning("read file error.[{}] does not exists.", full_path)
      return None
    
    with open(full_path, mode=mode) as f:
      return f.read()
  
  def readAsJson(self, path):
    content = self.read(path)
    if content is None:
      return content
    return json.loads(content)

  def write(self, path, content, mode="w+"):
    full_path = self.get_full_path(path)
    dir_path = os.path.dirname(full_path)
    if not os.path.exists(dir_path):
      os.makedirs(dir_path)

    with open(full_path, mode=mode) as f:
      f.write(content)
  
  def writeAsJson(self, path, content):
    self.write(path, json.dumps(content))
