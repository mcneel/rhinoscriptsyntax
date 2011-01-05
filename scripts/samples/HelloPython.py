# Basic syntax for writing python scripts
print "Hello Python!"

# <- any line that begins with the pound symbol is a comment

# assign a variable
x=123
# print out the type of the variable
print type(x)
# print out the value of the variable
print x
# combine statements with commas to print a single line
print "x is a", type(x), " and has a value of", x

#loops
# notice that there is a colon at the end of the first line and
# and what is executed has some spaces in front of it
for i in range(1,10):
    print "i=",i

#conditionals
x = 8
for i in xrange(1,x+1):
    if i%2==0:
        print i," is even"
    else:
        print i," is odd"

#functions
def MyFunc(a):
    x = a+2
    print a,"+2=",x

MyFunc(10)
