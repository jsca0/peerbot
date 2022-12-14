from brownie import network, config, accounts

#
#   returns the bot-master's account
#
def get_account():
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])