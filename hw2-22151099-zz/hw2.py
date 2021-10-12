import requests
import hashlib
import binascii
import urllib.request
import json
import os

# target = '0000000000000000000022d8f11190d40de785dbf24bdfaa7d4040c804c5e507'
target = input('请输入需要验证的区块hash : ')

"""
验证区块哈希的正确性
"""
# 获取16进制区块信息
def get_hex_record(target):
    print('reading hex ...')
    url = 'https://blockchain.info/rawblock/' + target + '?format=hex'
    r = requests.get(url)
    print('reading hex complete ...')
    return r.text

hex_record = get_hex_record(target)

# 获取json格式的区块信息
def get_json_record(target):
    print('reading json ...')
    url = 'https://blockchain.info/rawblock/' + target
    resp = urllib.request.urlopen(url)
    js = json.loads(resp.read())
    print('reading json complete ...')
    return js

json_record = get_json_record(target)

# 展示区块信息
def show_info():
    print('区块信息 : ')
    print('hash : ' + json_record['hash'])
    print('ver : ' + str(json_record['ver']))
    print('prev_block : ' + json_record['prev_block'])
    print('mrkl_root : ' + json_record['mrkl_root'])
    print('time : ' + str(json_record['time']))
    print('bits : ' + str(json_record['bits']))
    print('nonce : ' + str(json_record['nonce']))
    print('')

# 计算区块哈希
def cal_hash():
    block_header = hex_record[:160]
    # print(block_header)
    hash = hashlib.sha256(hashlib.sha256(binascii.unhexlify(block_header)).digest()).digest()
    result = binascii.hexlify(hash[::-1]).decode('utf8')
    return result

# 验证区块哈希
def validate_hash():
    show_info()
    calculated_hash = cal_hash()
    print('calculated_hash = ' + calculated_hash)
    print('')
    print('block hash 验证结果 : ')
    if calculated_hash == target:
        print('block hash is right')
    else:
        print('block hash is wrong')
    print('===========================================================================')

"""
验证merkle_root正确性
"""
# 大端与小端互相转换
def big_small_end_trans(str):
    return binascii.hexlify(binascii.unhexlify(str)[::-1]).decode('utf8')

# 计算区块的merkle_root值
def cal_merkle_root():
    json_tx_record = json_record['tx']
    tx_nums = len(json_record['tx'])
    tx_hash = []
    print('开始读入交易hash ...')
    for i in range(tx_nums):
        if i % 100 == 0:
            print('reading %d hashs...'%i)
        tx_hash.append(big_small_end_trans(json_tx_record[i]['hash']))
    print('交易hash读取完毕 ...')
    print('')
    if tx_nums == 1:
        return tx_hash[0]

    print('开始计算merkle_tree内部各节点hash ...')
    while tx_nums != 1:
        index = 0
        new_index = 0
        while index < tx_nums:
            left = tx_hash[index]
            index += 1
            right = ''
            if index == tx_nums:
                right = left
            else:
                right = tx_hash[index]
                index += 1
            tx_hash[new_index] = binascii.hexlify(hashlib.sha256(hashlib.sha256(binascii.unhexlify(left + right)).digest()).digest()).decode('utf8')
            new_index += 1
        tx_hash = tx_hash[:new_index]
        tx_nums = new_index
        print('当前层的节点数量' + str(tx_nums))
    print('merkle_tree各节点hash计算完毕 ...')
    print('')
    return tx_hash[0]

# 验证merkle_root
def validate_merkle_root():
    calculated_merkle_root = big_small_end_trans(cal_merkle_root())
    print('calculated_merkle_root = ' + calculated_merkle_root)
    print('')
    print('merkle_root 验证结果 : ')
    if calculated_merkle_root == json_record['mrkl_root']:
        print('merkle root is right')
    else:
        print('merkle root is wrong')
    print('===========================================================================')

validate_hash()
validate_merkle_root()
os.system('pause')