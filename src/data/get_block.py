from data_utils import *
import pandas as pd
import os
import json
from datetime import datetime
#path
dir = os.environ.get('dir')
block_dir, meta_dir = dir + '/data/raw/blockdata', dir + '/data/raw/metadata'
def getHash(start, end, attack_file='timestamp.csv'):
    #env var
    os.environ['init_normal'] = "1"
    os.environ['init_attack'] = "1"
    def timestamp_hash(timestamp, cat='normal'):
        #init or cont' ?
        init = int(os.environ['init_normal']) if cat == 'normal' else int(os.environ['init_attack'])
        print(f"{timestamp}, init ?", bool(init))
        if os.path.exists(f"{meta_dir}/{cat}.json") and init:
            os.system(f"rm -rf {meta_dir}/{cat}.json")


        #save block hash of dates in metadata according to category
        save_file = f"{meta_dir}/{cat}.json" if init else f"{meta_dir}/temp.json"
        time_api = f"https://blockchain.info/blocks/{timestamp}?format=json"
        os.system(f"curl --http 1.1 {time_api} > {save_file}")
        #merge to main cat.json file
        if "temp" in save_file:
            main_dict = json.load(open(f"{meta_dir}/{cat}.json", 'r'))
            temp_dict = json.load(open(f"{meta_dir}/temp.json", 'r'))
            main_dict.extend(temp_dict)
            #dump back
            json.dump(main_dict, open(f"{meta_dir}/{cat}.json", 'w'), indent=3)
        #no longer init
        if cat == 'normal':
            os.environ['init_normal'] = "0"
        else:
            os.environ['init_attack'] = "0"


    #get attack list:
    attack_df = pd.read_csv(f'{meta_dir}/{attack_file}')
    attack_list = attack_df['dosday'].tolist()

    #get all day we analyze
    allday_list = get_date(start, end)



    #divide into 2 cats
    record_file = open(f"{meta_dir}/record.txt", 'w')
    for timestamp in allday_list:
        record_file.write(str(timestamp) + '\n')
        if timestamp in attack_list:
            timestamp_hash(timestamp, cat='attack')
        else:
            timestamp_hash(timestamp, cat='normal')

def getBlock():
    if os.path.exists(f"{block_dir}/{cat}.json"):
        os.environ['init_normal'] = "0"
        os.environ['init_attack'] = "0"
    else:
        os.environ['init_normal'] = "1"
        os.environ['init_attack'] = "1"
    def hash_block(hash, cat='normal'):
        #init or cont' ?
        init = int(os.environ['init_normal']) if cat == 'normal' else int(os.environ['init_attack'])


        #save block hash of dates in metadata according to category
        save_file = f"{block_dir}/{cat}.json" if init else f"{block_dir}/temp.json"
        block_api = f"https://blockchain.info/rawblock/{hash}"
        os.system(f"curl {block_api} > {save_file}")
        #merge to main cat.json file
        if "temp" in save_file:
            main_dict = json.load(open(f"{block_dir}/{cat}.json", 'r'))
            if isinstance(main_dict, dict):
                main_dict = [main_dict]
            temp_dict = json.load(open(f"{block_dir}/temp.json", 'r'))
            main_dict.append(temp_dict)
            #dump back
            json.dump(main_dict, open(f"{block_dir}/{cat}.json", 'w'), indent=3)
        #no longer init
        if cat == 'normal':
            os.environ['init_normal'] = "0"
        else:
            os.environ['init_attack'] = "0"

    record_write = open(f"{meta_dir}/record.txt", 'w')
    record_read = [hash.strip() for hash in open(f"{meta_dir}/record.txt", 'r').readlines()]
    for cat in ['normal', 'attack']:
        for data in json.load(open(f"{meta_dir}/{cat}.json", 'r')):
            hash = data['hash']
            if hash in record_read:
                continue

            #record this file:
            record_write.write(str(hash) + '\n')
            hash_block(hash, cat)

    


    
if __name__ == '__main__':
    #timestamp file
    attack_file = 'timestamp.csv'
    #time period
    start, end = '2011-02-01', '2013-10-31'
    #attack timestamp
    get_timestamp(attack_file)
    # get hash
    # getHash(start=start, end=end, attack_file=attack_file)
    #get block info
    getBlock()

