import requests


def get_balance(wallet_address):
 
    # API endpoint URL for retrieving wallet balance from blockchain.com API
    balance_url = "https://live.blockcypher.com/btc-testnet/address/" + wallet_address


    # Make API request to retrieve wallet balance
    response = requests.get(balance_url)

    response_text = response.text
    index =  response_text.find("balance of")
    balance = float(response_text[index+11:index + 18])
    return balance

       # Wallet address
   
address = "tb1qud9u85mcjcwndgwjqgcw69neah9z22kp7uw9wv" #Attacker crypto wallet address

get_balance(address)