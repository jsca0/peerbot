#source: https://github.com/bmuller/kademlia
import asyncio

from kademlia.network import Server
from src.Util.logger import get_logger

log = get_logger('kademlia')

loop = asyncio.get_event_loop()
loop.set_debug(True)

server = Server()
loop.run_until_complete(server.listen(8468))

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    server.stop()
    loop.close()