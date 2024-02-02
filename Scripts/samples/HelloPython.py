# Basic syntax for writing python scripts
print("Hello Python!")

# <- any line that begins with the pound symbol is a comment

# assign a variable
x=123
# print out the type of the variable
print(type(x))
# print out the value of the variable
print(x)
# combine statements with commas to print a single line
print("x is a {} and has a value of {}".format(type(x), x))

#loops
# notice that there is a colon at the end of the first line and
# and what is executed has some spaces in front of it
for i in range(1,10):
    print("i={}".format(i))

#conditionals
x = 8
for i in range(1,x+1):
    if i%2==0:
        print("{} is even".format(i))
    else:
        print("{} is odd".format(i))

#functions
def MyFunc(a):
    x = a+2
    print("{}+2={}".format(a,x))

MyFunc(10)
