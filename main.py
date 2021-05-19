import random
import requests
import json
from datetime import datetime
import hashlib


def load_data():
    """
    Load data from mining server
    :return: http response text
    """
    request = requests.get('http://localhost:8080/api/coingame/state')
    if request.status_code == 200:
        return request.text
    else:
        return

def parse_data(content):
    """
    Convert http initial digest response to JSON
    :param content: response from webserver for initial digest calculation
    :return: JSON
    """
    return json.loads(content)

def get_target_pattern(level = 1):
    """
    Returns string filling by 4-digit zero's char for requested difficulty

    :param level: difficulty
    :return:
    """
    return "".zfill(level)

def is_difficulty_level(digest, level = 1):
    """
    Testing of new digest for requested number of leading zeros
    :param digest: new calculated digest
    :param level: requested difficulty
    :return: True when new digest contains requested number of leading zeros
    """
    return digest[0:level] == get_target_pattern(level)

def calc_new_hash(previous_digest, block):
    """
    Calculate new digest for previous digest and yaml block
    :param previous_digest: last valid digest
    :param block: yaml block
    :return: new string with new digest
    """
    m = hashlib.sha384()
    m.update(previous_digest.encode('utf-8'))
    m.update(block.encode('utf-8'))
    m.update(previous_digest.encode('utf-8'))
    m.update(block.encode('utf-8'))
    return m.hexdigest()

def create_new_block(digest, difficulty, nonce, miner, fee):
    """
    Prepare yaml string for digest calculation
    :param digest:
    :param difficulty:
    :param nonce:
    :param miner:
    :param fee:
    :return:
    """

    timestamp = datetime.now().isoformat() + "Z"
    return \
    "--- !Hash\n" \
    f"Digest: '{digest}'\n" \
    f"--- !Hash\n" \
    f"Timestamp: {timestamp}\n" \
    f"Difficulty: {difficulty}\n" \
    f"Nonce: {nonce}\n" \
    f"Miner: {miner}\n" \
    f"Transactions:\n" \
    f"  - !Transaction\n" \
    f"    Fee: {fee}\n"

def get_bin_digest(digest, level):
    """
    Convert every char of hex string to 4-digit binary string representation
    Example: digest = "0F", level = 1 returns 0000
    Example: digest = "0F", level = 2 returns 00001111
    :param digest: input hex string
    :param level: max of binary 4-digit occurencies
    :return: string
    """
    out = ""
    for digit in digest:
        out += bin(int(digit, 16))[2:].zfill(4)
        if len(out) >= level:
            break
    return out

def create_final_block(new_block, new_digest):
    """
    Create final yaml for computing block and new digest
    :param new_block:
    :param new_digest:
    :return:
    """
    final_block = f"--- !Hash\nDigest: '{new_digest}'\n"
    return new_block + final_block

def save_data(final_block):
    """
    Put new digest on the server
    :param final_block:
    :return: requests.response as text
    """
    r = requests.put('http://localhost:8080/api/coingame', data=final_block, headers={'Content-Type': 'text/plain'})
    return r.text

# Init
random.seed()
# Load initial digest
content = load_data()
data = parse_data(content)
digest = data["Digest"]
difficulty = data["Difficulty"]
fee = data["Fee"]
miner = "stebur"

#difficulty = 3 #for debug purpose only

print('Start new hash calculation for difficulty {} and fee {}'.format(difficulty, fee))
iteration = 0
found = False
while True:
    nonce = random.randint(1, 99999999)
    my_block = create_new_block(digest, difficulty, nonce, miner, fee)
    new_digest = calc_new_hash(digest, my_block)
    if is_difficulty_level(new_digest, difficulty):
        print('Found new hash', new_digest)
        found = True
        break
    else:
        iteration += 1
        #print(iteration, new_digest)
        if iteration > 50000000:
            print('Stop due of iteration limit {}'.format(iteration))
            break
        elif iteration % 100000 == 0:
            print("iteration ", iteration)

if found:
    final_block = create_final_block(my_block, new_digest)
    print(save_data(final_block))






