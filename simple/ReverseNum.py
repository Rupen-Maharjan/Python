def rev(val):
    if val<10:
        return val
    else:
        digit=len(str(val//10))
        return (val%10) * (10**digit) +rev(val//10)

print(rev(1222))
