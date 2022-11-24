# Imports
from web3.gas_strategies.time_based import medium_gas_price_strategy


def get_balance(w3, account):
    # Get balance of address in Wei
    wei_balance = w3.eth.get_balance(account)

    # Return the value in wei
    return wei_balance


def send_transaction(w3, from_account, to_account, amount, private_key):

    # Set gas price strategy
    w3.eth.setGasPriceStrategy(medium_gas_price_strategy)

    # build a transaction in a dictionary
    raw_tx = {
        'to': to_account,
        'from': from_account,
        'value': int(amount),
        'gas': w3.eth.estimateGas({"to": to_account, "from": from_account, "value": int(amount)}),
        'gasPrice': 0,
        'nonce': w3.eth.getTransactionCount(from_account)
    }

    # sign the transaction
    signed_tx = w3.eth.account.sign_transaction(raw_tx, private_key)

    # send transaction
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)


    # Send the signed transactions
    return tx_hash

