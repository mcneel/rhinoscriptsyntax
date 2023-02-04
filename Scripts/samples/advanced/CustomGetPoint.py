# A Rhino GetPoint that performs some custom dynamic drawing
import Rhino
import System.Drawing
import scriptcontext

def CustomArc3Point():
    # Color to use when drawing dynamic lines
    line_color = System.Drawing.Color.FromArgb(255,0,0)
    arc_color = System.Drawing.Color.FromArgb(150,0,50)

    rc, pt_start = Rhino.Input.RhinoGet.GetPoint("Start point of arc", False)
    if( rc!=Rhino.Commands.Result.Success ): return
    rc, pt_end = Rhino.Input.RhinoGet.GetPoint("End point of arc", False)
    if( rc!=Rhino.Commands.Result.Success ): return

    # This is a function that is called whenever the GetPoint's
    # DynamicDraw event occurs
    def GetPointDynamicDrawFunc( sender, args ):
        #draw a line from the first picked point to the current mouse point
        args.Display.DrawLine(pt_start, args.CurrentPoint, line_color, 2)
        #draw a line from the second picked point to the current mouse point
        args.Display.DrawLine(pt_end, args.CurrentPoint, line_color, 2)
        #draw an arc through these three points
        arc = Rhino.Geometry.Arc(pt_start, args.CurrentPoint, pt_end)
        args.Display.DrawArc(arc, arc_color, 1)

    # Create an instance of a GetPoint class and add a delegate
    # for the DynamicDraw event
    gp = Rhino.Input.Custom.GetPoint()
    gp.DynamicDraw += GetPointDynamicDrawFunc
    gp.Get()
    if( gp.CommandResult() == Rhino.Commands.Result.Success ):
        pt = gp.Point()
        arc = Rhino.Geometry.Arc(pt_start,pt,pt_end)
        scriptcontext.doc.Objects.AddArc(arc)
        scriptcontext.doc.Views.Redraw()


if( __name__ == "__main__" ):
    CustomArc3Point()