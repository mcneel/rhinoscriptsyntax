# The following sample shows how to creates a custom windows form
# with a textbox that can be used to define the text in a new text dot
from System.Windows.Forms import Form, DialogResult, Label, Button, TextBox
from System.Drawing import Point, Size
import rhinoscript.selection
import rhinoscript.geometry

# Our custom form class
class AnnotateForm(Form):
  # build all of the controls in the constructor
  def __init__(self, curveId):
    offset = 10
    self.Text = "Annotate Curve"
    crvlabel = Label(Text="Curve ID = "+str(curveId), AutoSize=True)
    self.Controls.Add(crvlabel)
    width = crvlabel.Right
    pt = Point(crvlabel.Left,crvlabel.Bottom + offset)
    labelstart = Label(Text="Text at start", AutoSize=True)
    labelstart.Location = pt
    self.Controls.Add(labelstart)
    pt.X = labelstart.Right + offset
    inputstart = TextBox(Text="Start")
    inputstart.Location = pt
    self.Controls.Add(inputstart)
    if( inputstart.Right > width ):
      width = inputstart.Right
    self.m_inputstart = inputstart

    pt.X  = labelstart.Left
    pt.Y  = labelstart.Bottom + offset*3
    buttonApply = Button(Text="Apply", DialogResult=DialogResult.OK)
    buttonApply.Location = pt
    self.Controls.Add(buttonApply)
    pt.X = buttonApply.Right + offset
    buttonCancel = Button(Text="Cancel", DialogResult=DialogResult.Cancel)
    buttonCancel.Location = pt
    self.Controls.Add(buttonCancel)
    if( buttonCancel.Right > width ):
      width = buttonCancel.Right
    self.ClientSize = Size(width, buttonCancel.Bottom)
    self.AcceptButton = buttonApply
    self.CancelButton = buttonCancel
  
  def TextAtStart(self):
    return self.m_inputstart.Text


# prompt the user to select a curve
curveId = rhinoscript.selection.GetObject("Select a curve",rhinoscript.selection.filter.curve)
if( curveId==None ):
  print "no curve selected"
else:
  location = rhinoscript.curve.CurveStartPoint(curveId)
  if( location!=None ):
    form = AnnotateForm(curveId)
    if( form.ShowDialog() == DialogResult.OK ):
      # this block of script is run if the user pressed the apply button
      text = form.TextAtStart()
      if( len(text) > 0 ):
        #create a new text dot at the start of the curve
        rhinoscript.geometry.AddTextDot(text, location)
