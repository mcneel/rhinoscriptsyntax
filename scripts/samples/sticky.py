# The scriptcontext module contains a standard python dictionary called
# sticky which "sticks" around during the running of Rhino. This dictionary
# can be used to save settings between execution of your scripts and then
# get at those saved settings the next time you run your script -OR- from
# a completely different script.
import rhinoscriptsyntax as rs
import scriptcontext


stickyval = 0
# restore stickyval if it has been saved
if scriptcontext.sticky.has_key("my_key"):
    stickyval = scriptcontext.sticky["my_key"]
nonstickyval = 12

print "sticky =", stickyval
print "nonsticky =", nonstickyval

val = rs.GetInteger("give me an integer")
if val:
    stickyval = val
    nonstickyval = val

# save the value for use in the future
scriptcontext.sticky["my_key"] = stickyval

