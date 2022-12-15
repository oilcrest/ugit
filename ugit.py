#ugit
# Get Github Updated micropython update

import os
import urequests
import json
import hashlib
import machine
import time
import ugit_config

global tree

# CHANGE TO YOUR REPOSITORY INFO
# Also check out my friends amazing work
user = ugit_config.user
repository = ugit_config.repository

# Static URLS
# GitHub uses main instead of master for python repository trees
giturl = 'https://github.com/{user}/{repository}'
call_trees_url = f'https://api.github.com/repos/{user}/{repository}/git/trees/main?recursive=1'
raw = f'https://raw.githubusercontent.com/{user}/{repository}/master/'

def pull(f_path,giturl=giturl):
  #files = os.listdir()
  r = urequests.get(giturl)
  try:
    new_file = open(f_path, 'w')
    new_file.write(r.content.decode('utf-8'))
    new_file.close()
  except:
    print('decode fail try adding non-code files to .gitignore')
    try:
      new_file.close()
    except:
      print('tried to close new_file to save memory durring raw file decode')
  
def pull_all_files(tree=call_trees_url,raw = raw):
  os.chdir('/')
  internal_tree = build_internal_tree()
  # Github Requires user-agent header otherwise 403
  r = urequests.get(tree,headers={'User-Agent': 'ugit-turfptax'})
  # Turn Githubs tree into a python dict
  tree = json.loads(r.content.decode('utf-8'))
  check = []
  # download and save all files
  for i in tree['tree']:
    if i['type'] == 'tree':
      try:
        os.mkdir(i['path'])
      except:
        print('failed to make directory may already exist')
    elif i['path'] != '.gitignore':
      try:
        os.remove(i['path'])
      except:
        print('failed to delete old file')
      try:
        internal_tree.remove(i['path'])
      except:
        print(f'{i["path"]} not in internal_tree')
        check.append(f'{i["path"]} not in internal_tree')
      pull(i['path'],raw + i['path'])
      try:
        check.append(i['path'] + ' updated')
      except:
        print('no slash or extension ok')
  # delete files not in Github tree
  if len(internal_tree) != 0:
    for i in internal_tree:
      try:
        os.remove(i[0])
      except:
        print(f'failed to delete: {i[0]}')
        check.append(f'{i[0]} failed to delete')
  logfile = ('ugit_log.py','w')
  logfile.write(str(check))
  logfile.close()
  time.sleep(10)
  machine.reset()
  #return check instead return with global

  
def build_internal_tree():
  global tree
  tree = []
  os.chdir('/')
  for i in os.listdir():
    add_to_tree(i)
  return(tree)

def add_to_tree(f_path):
  global tree
  try:
    folder = os.listdir(f_path)
  except:
    folder = False
  if not folder:
    print(f_path)
    subfile_path = os.getcwd() + '/' + f_path
    tree.append([subfile_path,get_hash(subfile_path)])
  else:
    if os.listdir(f_path):
      os.chdir(f_path)
      for i in folder:
        add_to_tree(i)
      os.chdir('..')
    else:
      print(f'{f_path} folder is empty')
  
def get_hash(file):
  print(file)
  o_file = open(file)
  r_file = o_file.read()
  sha1obj = hashlib.sha1(r_file)
  hash = sha1obj.digest()
  return(hash.hex())
  
