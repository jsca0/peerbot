import asyncio

from kademlia.network import Server

from ThreadedEventLoop import ThreadedEventLoop

#
# Storage_Network using Kademlia
#
class KademliaStorageNetwork:
    def __init__(self, bootstrap) -> None:
        self._loop = None
        self._node, self.id = self.connect(bootstrap)


    #
    #   Submits node.set to run in the event loop safely
    #
    #   return a Future 
    #
    def store(self, item):
        t = asyncio.run_coroutine_threadsafe(self._node.set(self.id, item), self._loop)
       

    #TODO
    def fetch(self, file_key):
        pass

    #
    #   connect to the Kadmlia network, using 'bootstrap'
    #   runs event loop in separate, background thread
    #
    #   return Kademlia node, node ID (Worker Key)
    #
    def connect(self, bootstrap):
        self._loop = asyncio.new_event_loop()
        node = Server()

        try:
            self._loop.run_until_complete(node.listen(8467))
            self._loop.run_until_complete(node.bootstrap(bootstrap))

            self._run_background_loop()
        except:
            pass #TODO
        
        return node, node.node.id.hex()
    
    def _run_background_loop(self):
        asyncio_thread = ThreadedEventLoop(self._loop)
        asyncio_thread.start()
 
    
    def stop(self):
        self._node.stop()