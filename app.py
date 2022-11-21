import os
import json
from web3 import Web3
from web3.gas_strategies.time_based import medium_gas_price_strategy
from pathlib import Path
from dotenv import load_dotenv
import math
import streamlit as st

from ttf_wallet import get_balance
from ttf_wallet import send_transaction


load_dotenv('ttf.env')

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Set the contract address (this is the address of the deployed contract)
tokentimefund_contract_address = os.getenv("TOKENTIMEFUND_ADDRESS")
tokentimefundcrowdsale_contract_address = os.getenv("TOKENTIMEFUNDCROWDSALE_ADDRESS")

################################################################################
# Contract Helper function:
# 1. Loads the contract once using cache
# 2. Connects to the contract using the contract address and ABI
################################################################################


@st.cache(allow_output_mutation=True)
def load_contract():

    # Load the TokenTimeFund contract ABI
    with open(Path('./contracts/compiled/TokenTimeFund_abi.json')) as f:
        tokentimefund_contract_abi = json.load(f)

    # Load the TokenTimeFundCrowdsale contract ABI
    with open(Path('./contracts/compiled/TokenTimeFundCrowdsale_abi.json')) as f:
        tokentimefundcrowdsale_contract_abi = json.load(f)       

    # Get the tokentimefund contract
    tokentimefund_contract = w3.eth.contract(
        address=tokentimefund_contract_address,
        abi=tokentimefund_contract_abi
    )

    # Get the tokentimefundcrowdsale contract
    tokentimefundcrowdsale_contract = w3.eth.contract(
        address=tokentimefundcrowdsale_contract_address,
        abi=tokentimefundcrowdsale_contract_abi
    )   

    return tokentimefund_contract, tokentimefundcrowdsale_contract

# Load the contracts
tokentimefund_contract, tokentimefundcrowdsale_contract = load_contract()


# Use of accounts from Ganache:
# Account 0 - not used
# Account 1 - dummy wallet to help simulate asset under management increase/decrease
# Account 2 - for deploying contracts using Remix and Metamask
# Account 3 - for asset under management/wei raised
# Account 4 - for TTF tokens bought back from investors, to be burnt
# Account 5 to 9 - Investors accounts
accounts = w3.eth.accounts
investors_accounts = accounts[5:10]

# Load AUM Wallet (acccounts[3]) address and private key
aum_wallet_address = accounts[3]
aum_wallet_private_key = os.getenv('AUMWALLET_PRIVATE_KEY')
dummy_wallet_private_key = os.getenv('DUMMYWALLET_PRIVATE_KEY')

# Set burn wallet address
burn_wallet_address = accounts[4]

# Show title of webpage
st.sidebar.title("Token Time Fund")

# Show fund information on sidebar
st.sidebar.markdown("## Token Time Fund Information")

# Show total TTF token supply
st.sidebar.write('Total TTF token supply:')
total_supply_placeholder = st.sidebar.empty()
total_supply = tokentimefund_contract.functions.totalSupply().call()
total_supply_placeholder.markdown('{:,}'.format(total_supply))
st.sidebar.write(tokentimefund_contract_address)
st.sidebar.write('')
st.sidebar.write('')

# Show total asset under management in sidebar. wei raised goes into this account
st.sidebar.write('Asset Under Management (in Wei):')
aum_placeholder = st.sidebar.empty()
# aum = tokentimefundcrowdsale_contract.functions.weiRaised().call()
aum = int(get_balance(w3, aum_wallet_address)) - 100000000000000000000
aum_placeholder.markdown('{:,}'.format(aum))
st.sidebar.write(aum_wallet_address)

# Show amount of tokens in burn wallet
st.sidebar.write('')
st.sidebar.write('')
tokens_burn_wallet = tokentimefund_contract.functions.balanceOf(burn_wallet_address).call()
st.sidebar.write('Number of tokens in burn wallet:')
burn_balance_placeholder = st.sidebar.empty()
burn_balance_placeholder.markdown('{}'.format(tokens_burn_wallet))
st.sidebar.write(burn_wallet_address)

st.sidebar.markdown("---")

st.sidebar.write('For use by Fund Manager. Automated in actual implementation.')

# Simulated. Manual burning of token. In actual implementation, burning will be done automatically
tokens_burn_placeholder = st.sidebar.empty()
tokens_amount_to_burn = tokens_burn_placeholder.text_input("Enter number of tokens to burn:", value="0")
if st.sidebar.button("Burn"):
    tx_hash = tokentimefund_contract.functions.burn(int(tokens_amount_to_burn)).transact({'from': burn_wallet_address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.sidebar.write('Blockchain transaction receipt:', tx_receipt)

    # Update displayed information
    total_supply = tokentimefund_contract.functions.totalSupply().call()
    total_supply_placeholder.markdown('{:,}'.format(total_supply))
    tokens_burn_wallet = tokentimefund_contract.functions.balanceOf(burn_wallet_address).call()
    burn_balance_placeholder.markdown('{}'.format(tokens_burn_wallet))

st.sidebar.markdown("---")

# Simulated. Change in value of fund. In actual implementation, changes in value will be done automatically
fund_value_change_placeholder = st.sidebar.empty()
fund_value_change = fund_value_change_placeholder.text_input("Change in %:", value="0")
if st.sidebar.button("Change"):
    change_pct = float(fund_value_change)/100
    aum_change = int(math.floor(float(aum) * change_pct))

    if aum_change > 0:
        ## transfer wei from dummy_wallet (accounts[1]) to AUM wallet
        tx_hash = send_transaction(w3, accounts[1], aum_wallet_address, aum_change, dummy_wallet_private_key)
        st.sidebar.write(tx_hash)
    
    elif aum_change < 0:
        ## transfer wei from AUM wallet to dummy_wallet (accounts[1])
        tx_hash = send_transaction(w3, aum_wallet_address, accounts[1], abs(aum_change), aum_wallet_private_key)
        st.sidebar.write(tx_hash)

    # Update info on display
    aum = int(get_balance(w3, aum_wallet_address)) - 100000000000000000000
    aum_placeholder.markdown('{:,}'.format(aum))


# Investors panel

# calculate conversion rate 
if total_supply > 0:
    conversion_rate = aum/total_supply
else:
    conversion_rate = 1

st.write('1 ETH = 1000000000000000000 wei')
st.markdown('Conversion rate: 1 token = {} wei'.format(round(conversion_rate,2)))
st.write('')
st.write('')

address = st.selectbox("Select Investor Account:", options=investors_accounts)
account_balance = w3.eth.getBalance(address)
account_number = w3.eth.accounts.index(address)

# wei balance streamlit placeholder
wei_balance_placeholder = st.empty() 

# ttf balance streamlit placeholder
ttf_balance_placeholder = st.empty()

wei_balance_placeholder.markdown('Wei balance: {}'.format(account_balance))
token_balance = tokentimefund_contract.functions.balanceOf(address).call()
ttf_balance_placeholder.markdown('TTF token balance: {}'.format(token_balance))

# Button that forces page to reload to clear hash messages
if st.button("Reload Page"):
    x = 1  # dummy

st.markdown("---")


# Buy tokens

buy_input_placeholder = st.empty()  # placeholder for text input
tokens_amount_to_buy = buy_input_placeholder.text_input("Enter number of tokens to buy:", value="0")
if st.button("Buy"):

    tx_hash = tokentimefundcrowdsale_contract.functions.buyTokens(address).transact({'from': address, 'value':int(tokens_amount_to_buy)})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write('Blockchain transaction receipt:', tx_receipt)

    ## Update information on webpage
    total_supply = tokentimefund_contract.functions.totalSupply().call()
    total_supply_placeholder.markdown('{:,}'.format(total_supply))
    # total_wei_raised = tokentimefundcrowdsale_contract.functions.weiRaised().call()
    aum = int(w3.eth.getBalance(aum_wallet_address)) - 100000000000000000000
    aum_placeholder.markdown('{:,}'.format(aum))
    account_balance = w3.eth.getBalance(address)
    wei_balance_placeholder.markdown('Wei balance: {}'.format(account_balance))
    token_balance = tokentimefund_contract.functions.balanceOf(address).call()
    ttf_balance_placeholder.markdown('TTF token balance: {}'.format(token_balance))

st.markdown("---")

# Sell tokens

sell_input_placeholder = st.empty() # placeholder for text input
tokens_amount_to_sell = sell_input_placeholder.text_input("Enter number of tokens to sell:", value="0")
if st.button("Sell"):

    ## transfer tokens from investor wallet to AUM wallet
    tx_hash = tokentimefund_contract.functions.transfer(accounts[4], int(tokens_amount_to_sell)).transact({'from': address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write('Blockchain transaction receipt:', tx_receipt)

    ## transfer wei from AUM wallet to investor wallet
    amount_to_transfer = int(math.floor(float(tokens_amount_to_sell) * conversion_rate))
    tx_hash = send_transaction(w3, aum_wallet_address, address, amount_to_transfer, aum_wallet_private_key)
    st.write(tx_hash)

    ## Update information on webpage
    aum = int(w3.eth.getBalance(aum_wallet_address)) - 100000000000000000000
    aum_placeholder.markdown('{:,}'.format(aum))
    tokens_burn_wallet = tokentimefund_contract.functions.balanceOf(accounts[4]).call()
    burn_balance_placeholder.markdown('{}'.format(tokens_burn_wallet))
    account_balance = w3.eth.getBalance(address)
    wei_balance_placeholder.markdown('Wei balance: {}'.format(account_balance))
    token_balance = tokentimefund_contract.functions.balanceOf(address).call()
    ttf_balance_placeholder.markdown('TTF token balance: {}'.format(token_balance))



### TO DO
# 1. simulate increase or decrease of AUM wallet due to portforlio performance by moving wei in or out of AUM wallet
# 2. change the value of tokens by changing the wei-token rate
