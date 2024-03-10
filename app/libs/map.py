class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v
        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

def map_merge(a, b, path=None, update=True):
  "http://stackoverflow.com/questions/7204805/python-dictionaries-of-dictionaries-merge"
  "merges b into a"
  if path is None: path = []
  for key in b:
      if key in a:
          if isinstance(a[key], dict) and isinstance(b[key], dict):
              map_merge(a[key], b[key], path + [str(key)])
          elif a[key] == b[key]:
              pass # same leaf value
          elif isinstance(a[key], list) and isinstance(b[key], list):
              for idx, val in enumerate(b[key]):
                  a[key][idx] = map_merge(a[key][idx], b[key][idx], path + [str(key), str(idx)], update=update)
          elif update:
              a[key] = b[key]
          else:
              raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
      else:
          a[key] = b[key]
  
  return a
