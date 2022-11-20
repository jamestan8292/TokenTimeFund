import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

load_dotenv('ttf.env')

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

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

    # Set the contract address (this is the address of the deployed contract)
    tokentimefund_contract_address = os.getenv("TOKENTIMEFUND_ADDRESS")
    tokentimefundcrowdsale_contract_address = os.getenv("TOKENTIMEFUNDCROWDSALE_ADDRESS")

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
# Account 0,1 - not used
# Account 2 - for deploying contracts using Remix and Metamask
# Account 3 - for Wei raised
# Account 4 - for TTF tokens bought back from investors, to be burnt
# Account 5 to 9 - Investors accounts
accounts = w3.eth.accounts
investors_accounts = accounts[5:9]


# Show title of webpage
st.title("Token Time Fund")

# Show fund information on sidebar
st.sidebar.markdown("## Token Time Fund Information")

# Show total TTF token supply
total_supply = tokentimefund_contract.functions.totalSupply().call()
st.sidebar.write('Total TTF token supply:')
st.sidebar.write('{:,}'.format(total_supply))
st.sidebar.write('')
st.sidebar.write('')

# Show total wei raised in sidebar
total_wei_raised = tokentimefundcrowdsale_contract.functions.weiRaised().call()
st.sidebar.write('Total Wei Raised:')
st.sidebar.write('{:,}'.format(total_wei_raised))
st.sidebar.write(accounts[3])

# Show amount of tokens in burn wallet
st.sidebar.write('')
st.sidebar.write('')
tokens_burn_wallet = tokentimefund_contract.functions.balanceOf(accounts[4]).call()
st.sidebar.write('Number of tokens in burn wallet:')
burn_balance = st.sidebar.empty()
burn_balance.write('{:,}'.format(tokens_burn_wallet))
st.sidebar.write(accounts[4])

st.sidebar.markdown("---")

tokens_amount_to_burn = st.sidebar.text_input("Enter number of tokens to burn:", value=0)
if st.sidebar.button("Burn"):
    tx_hash = tokentimefund_contract.functions.burn(int(tokens_amount_to_burn)).transact({'from': accounts[4]})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.sidebar.write('Blockchain transaction receipt:', tx_receipt)

    tokens_burn_wallet = tokentimefund_contract.functions.balanceOf(accounts[4]).call()
    burn_balance.write('{:,}'.format(tokens_burn_wallet))


# Investors panel

address = st.selectbox("Select Investor Account:", options=investors_accounts)
account_balance = w3.eth.getBalance(address)
account_number = w3.eth.accounts.index(address)

# wei balance streamlit placeholder
wei_balance = st.empty() 

# ttf balance streamlit placeholder
ttf_balance = st.empty()

wei_balance.markdown('Wei balance: {:,}'.format(account_balance))
token_balance = tokentimefund_contract.functions.balanceOf(address).call()
ttf_balance.markdown('TTF tokens balance: {:,}'.format(token_balance))

if st.button("Update Page"):
    x = 1

st.markdown("---")

# # Buy tokens
# tokens_amount = st.text_input("Enter amount of tokens", value=0)
# if st.button("Buy"):
#     tx_hash = tokentimefundcrowdsale_contract.functions.buyTokens(address).transact({'from': address, 'value':int(tokens_amount)})
#     tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
#     st.write('Blockchain transaction receipt:', tx_receipt)

#     wei_balance.markdown('Wei balance: {:,}'.format(account_balance))
#     token_balance = tokentimefund_contract.functions.balanceOf(address).call()
#     ttf_balance.markdown('TTF tokens balance: {:,}'.format(token_balance))

# st.markdown("---")

tokens_amount_to_buy = st.text_input("Enter number of tokens to buy:", value=0)
if st.button("Buy"):
    tx_hash = tokentimefundcrowdsale_contract.functions.buyTokens(address).transact({'from': address, 'value':int(tokens_amount_to_buy)})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write('Blockchain transaction receipt:', tx_receipt)

    wei_balance.markdown('Wei balance: {:,}'.format(account_balance))
    token_balance = tokentimefund_contract.functions.balanceOf(address).call()
    ttf_balance.markdown('TTF tokens balance: {:,}'.format(token_balance))

st.write('')
st.write('')

tokens_amount_to_sell = st.text_input("Enter number of tokens to sell:", value=0)
if st.button("Sell"):
    tx_hash = tokentimefund_contract.functions.transfer(accounts[4], int(tokens_amount_to_sell)).transact({'from': address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write('Blockchain transaction receipt:', tx_receipt)

    wei_balance.markdown('Wei balance: {:,}'.format(account_balance))
    token_balance = tokentimefund_contract.functions.balanceOf(address).call()
    ttf_balance.markdown('TTF tokens balance: {:,}'.format(token_balance))