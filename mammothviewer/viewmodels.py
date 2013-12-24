import collections


def view_model(attr_names):
    return ViewModel(attr_names)


class ViewModel(object):
    def __init__(self, attr_names):
        self._attrs = dict((name, None) for name in attr_names)
        self._listeners = collections.defaultdict(lambda: [])

    def __setattr__(self, key, value):
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            if key in self._attrs:
                self._attrs[key] = value
                self._notify(key, value)
            else:
                raise ValueError("Cannot set {0}".format(key))
    
    def __getattr__(self, key):
        return self._attrs[key]
    
    def on_change(self, key, listener):
        if key in self._attrs:
            self._listeners[key].append(listener)
        else:
            raise ValueError("Cannot listen for {0}".format(key))
    
    def _notify(self, key, value):
        for listener in self._listeners[key]:
            listener(value)
