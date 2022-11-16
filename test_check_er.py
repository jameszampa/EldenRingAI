import re

with open('check_er.txt', 'r') as f:
    for line in f.readlines():
        match = re.search(r'james +(\d+)', line)
        if not match is None:
            print(match[1])