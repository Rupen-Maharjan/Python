q=('who created this game?','what language is used to crate this game?','what is the gaming name of the creator?')
ans=('D','A','C')
l1=('Rocket','Robin','Ayush','Rupen')
l2=('Python','C++','C','Rust')
l3=('Rocket','IronMan','Discort','Kaya')
level=0
options=(l1,l2,l3)
gameOver=False

while(not gameOver):
    print(f'\nLevel {level+1}')
    print(q[level])
    print(f'\nOptions\nA:{options[level][0]}\t B:{options[level][1]}\t C:{options[level][2]}\t D:{options[level][3]}')
    user=input(': ')
    if (user==ans[level].lower()):
        level+=1
    else:
        print(f'\nGame Over!!\nLevel {level+1}')
        gameOver=True


    if (level==3):
        print('\nyu win!')
        gameOver=True
