import random

opt=('A:snake','B:water','C:gun')


print('Snake water gun game!')
print('Options:')

for i in opt:
    print(i)

com=random.choice(opt)
user=input(': ').lower()
print(f"{com.split(':')[1].lower()}")

com=com.split(':')[0].lower()
match (user,com):
    case ('a','b') | ('b','c') | ('c','a'):
        print('Player Wins!')
    case ('b','a') | ('c','b') | ('a','c'):
        print('Computer Win!')
    
    case _ if user==com:
        print('Draw!')
    case  _:
        print('Yu loose!')