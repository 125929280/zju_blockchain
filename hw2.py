import requests
import hashlib
import binascii
import urllib.request
import json

target = '00000000000000000001d1ac73631145c9f46a199fed8d4ae4f5e849d3581d09'

"""
验证区块哈希的正确性
"""
# 获取16进制区块信息
def get_hex_record(target):
    url = 'https://blockchain.info/rawblock/' + target + '?format=hex'
    r = requests.get(url)
    return r.text

# 获取json格式的区块信息
def get_json_record(target):
    url = 'https://blockchain.info/rawblock/' + target
    resp = urllib.request.urlopen(url)
    js = json.loads(resp.read())
    return js

# 展示区块信息
def show_info(target):
    json_record = get_json_record(target)
    print('hash : ' + json_record['hash'])
    print('ver : ' + str(json_record['ver']))
    print('prev_block : ' + json_record['prev_block'])
    print('mrkl_root : ' + json_record['mrkl_root'])
    print('time : ' + str(json_record['time']))
    print('bits : ' + str(json_record['bits']))
    print('nonce : ' + str(json_record['nonce']))

# 计算区块哈希
def cal_hash(target):
    hex_record = get_hex_record(target)
    block_header = hex_record[:160]
    print(block_header)
    hash = hashlib.sha256(hashlib.sha256(binascii.unhexlify(block_header)).digest()).digest()
    result = binascii.hexlify(hash[::-1]).decode('utf8')
    return result

# 验证区块哈希
def validate_hash(target):
    show_info(target)
    calculated_hash = cal_hash(target)
    print('calculated_hash = ' + calculated_hash)

    if calculated_hash == target:
        print('block hash is right')
    else:
        print('block hash is wrong')

"""
验证merkle_root正确性
"""
# 大端与小端互相转换
def big_small_end_trans(str):
    return binascii.hexlify(binascii.unhexlify(str)[::-1]).decode('utf8')

# 返回大端merkle_root
def get_merkle_root(target):
    json_record = get_json_record(target)
    return json_record['mrkl_root']

# 计算区块的merkle_root值
def cal_merkle_root(target):
    json_record = get_json_record(target)
    json_tx_record = json_record['tx']
    tx_nums = len(json_record['tx'])
    tx_hash = []
    for i in range(tx_nums):
        if i % 100 == 0:
            print('reading %d hashs...'%i)
        tx_hash.append(big_small_end_trans(json_tx_record[i]['hash']))

    if tx_nums == 1:
        return tx_hash[0]

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
    return tx_hash[0]

# 验证merkle_root
def validate_merkle_root(target):
    calculated_merkle_root = big_small_end_trans(cal_merkle_root(target))
    print('calculated_merkle_root = ' + calculated_merkle_root)
    if calculated_merkle_root == get_merkle_root(target):
        print('merkle root is right')
    else:
        print('merkle root is wrong')

validate_hash(target)
validate_merkle_root(target)