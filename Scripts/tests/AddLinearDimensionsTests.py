import rhinoscriptsyntax as rs
from scriptcontext import doc
import unittest
import Rhino

def coerceannotation(object_id):
    annotation_object = rs.coercerhinoobject(object_id, True)
    if not isinstance(annotation_object, Rhino.DocObjects.AnnotationObjectBase):
        raise ValueError("object_id does not refer to an Annotation")
    return annotation_object

class AddLinearDimensionsTests(unittest.TestCase):
  def test_CurrentCPlaneWithPointsOnPlane(self):
    plane = rs.WorldXYPlane()
    id = rs.AddLinearDimension(plane, (1,1,0), (11,1,0), (1,3,0))
    d = coerceannotation(id).Geometry
    ln1End = plane.PointAt(d.ExtensionLine1End.X, d.ExtensionLine1End.Y)
    ln2End = plane.PointAt(d.ExtensionLine2End.X, d.ExtensionLine2End.Y)
    self.assertTrue(rs.PointCompare(ln1End, (1,1,0), doc.ModelAbsoluteTolerance))
    self.assertTrue(rs.PointCompare(ln2End, (11,1,0), doc.ModelAbsoluteTolerance))

  def test_CurrentCPlaneWithFirstPointOffThePlane(self):
    plane = rs.WorldXYPlane()
    id = rs.AddLinearDimension(plane, (1,1,2), (11,1,0), (1,3,0))
    d = coerceannotation(id).Geometry
    ln1End = plane.PointAt(d.ExtensionLine1End.X, d.ExtensionLine1End.Y)
    ln2End = plane.PointAt(d.ExtensionLine2End.X, d.ExtensionLine2End.Y)
    self.assertTrue(rs.PointCompare(ln1End, (1,1,2), doc.ModelAbsoluteTolerance))
    self.assertTrue(rs.PointCompare(ln2End, (11,1,2), doc.ModelAbsoluteTolerance))

suite = unittest.TestLoader().loadTestsFromTestCase(AddLinearDimensionsTests)
unittestresult = unittest.TextTestRunner(verbosity=2).run(suite)
