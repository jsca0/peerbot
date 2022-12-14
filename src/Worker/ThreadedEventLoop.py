import asyncio
from asyncio import AbstractEventLoop
from threading import Thread

#
#   Runs an event loop in the background
#
class ThreadedEventLoop(Thread):
    def __init__(self, loop: AbstractEventLoop) -> None:
        super().__init__()
        self._loop = loop
        self.daemon =True

    def run(self):
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self._loop.close()
            