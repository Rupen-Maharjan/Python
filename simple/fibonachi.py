def febo(val):
    a,b=0,1
    print(a)
    print(b)
    for i in range(2,val):
        a,b=b,a+b
        print(b)

print('Program to print fibonaci numbers')
user=int(input(': '))
febo(user)