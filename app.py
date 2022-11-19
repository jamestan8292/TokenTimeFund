import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

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


st.title("Token Time Fund")
st.write("Choose an account to get started")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)
st.markdown("---")

