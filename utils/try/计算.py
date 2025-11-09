NUMBER_OF_ELEMENTS=int(input("Enter the number of integers:"))

s=input("Enter the integers between 1 and 100:")

items=s.split()

table=[eval(x) for x in items]

for i in range(0,NUMBER_OF_ELEMENTS):

    a=table[i]

    count=0

    for j in range(0,NUMBER_OF_ELEMENTS):

        if table[j]==a:

            count+=1

    print(a," occurs ",count," times")