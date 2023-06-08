import requests
import re


def get_balance(wallet_address):
 
    # API endpoint URL for retrieving wallet balance from blockchain.com API
    balance_url = "https://live.blockcypher.com/btc-testnet/address/" + wallet_address
    decimal_pattern = r'\d+\.\d+'


    # Make API request to retrieve wallet balance
    response = requests.get(balance_url)
    if response.status_code == 200:
        response_text = response.text
        index =  response_text.find("balance of")
        balance_str = response_text[index+11:index + 20]
        print(balance_str)
        match = re.search(decimal_pattern, balance_str)
        balance = float(match.group())
        return balance

       # Wallet address
   
address = "tb1qud9u85mcjcwndgwjqgcw69neah9z22kp7uw9wv" #Attacker crypto wallet address

print(get_balance(address))
