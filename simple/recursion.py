def sumD(val):
    if val ==0:
        return 0
    return (val %10) + sumD(val//10)

user=int(input(': '))
print(sumD(user))