import string
import random

c = int(input('1:encrypt\n2:decrypt\n: '))

user = input('Message: ')
sy = ''.join(random.choice(string.punctuation) for _ in range(10))
lt = ''.join(random.choice(string.ascii_letters) for _ in range(10))

def enc(msg): 
    space_positions = [i for i, ch in enumerate(msg) if ch == " "]
    msg_nospace = msg.replace(" ", "")


    if len(msg_nospace) >= 3:
        rev = msg_nospace[2:] + msg_nospace[:2]
    else:
        rev = msg_nospace[1:] + msg_nospace[:1]

    rev_list = list(rev)
    for pos in space_positions:
        rev_list.insert(pos, " ")
    rev = "".join(rev_list)

    e = sy[:5] + lt[:5] + rev + sy[5:] + lt[5:]
    print("Encrypted:", e)
    return e, space_positions

def dec(msg):
    org = msg[10:len(msg)-10]

    space_positions = [i for i, ch in enumerate(org) if ch == " "]
    org_nospace = org.replace(" ", "")

    if len(org_nospace) >= 3:
        rev = org_nospace[-2:] + org_nospace[:-2]
    else:
        rev = org_nospace[-1:] + org_nospace[:-1]

    rev_list = list(rev)
    for pos in space_positions:
        rev_list.insert(pos, " ")
    rev = "".join(rev_list)

    print("Decrypted:", rev)
    return rev

if c == 1:
    enc(user)
elif c == 2:
    dec(user)
else:
    print('invalid')
