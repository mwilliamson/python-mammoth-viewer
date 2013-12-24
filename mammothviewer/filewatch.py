import os
import threading
import time


class FileWatcher(object):
    _POLL_INTERVAL = 1
    
    def __init__(self, paths, func):
        self._paths = paths
        self._func = func
        self._thread = None
        self._last_modified_times = self._generate_last_modified_times()
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
            modified_times = self._generate_last_modified_times()
            if modified_times != self._last_modified_times:
                self._last_modified_times = modified_times
                self._func()
            time.sleep(self._POLL_INTERVAL)
    
    def _generate_last_modified_times(self):
        return dict(
            (path, os.stat(path).st_mtime)
            for path in self._paths
        )
