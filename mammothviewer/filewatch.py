import os
import threading
import time


class FileWatcher(object):
    _POLL_INTERVAL = 1
    
    def __init__(self, path, func):
        self._path = path
        self._func = func
        self._thread = None
        self._last_modified_time = os.stat(self._path).st_mtime
        self._shutdown = False
    
    def start(self):
        self._thread = threading.Thread(target=self._watch)
        self._thread.start()
        
    def stop(self):
        self._shutdown = True
    
    def join(self):
        self._thread.join()
        
    def _watch(self):
        while not self._shutdown:
            modified_time = os.stat(self._path).st_mtime
            if modified_time > self._last_modified_time:
                self._last_modified_time = modified_time
                self._func()
            time.sleep(self._POLL_INTERVAL)
