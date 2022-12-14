from KademliaStorageNetwork import KademliaStorageNetwork
from Util.logger import *

CONFIG_FILE = "botnet_config.yaml"
BOOTSTRAP = [("127.0.0.1", 8468)]
RPC_URL = 'https://rinkeby.infura.io/v3/4675ebf76f20409eb8a6e7a296ac4a8a'

storage_net = KademliaStorageNetwork(BOOTSTRAP) #make new kadmlia node