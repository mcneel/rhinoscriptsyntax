import unittest
import uuid

import Rhino
import Rhino.Geometry as g

import rhinoscriptsyntax as rs
import scriptcontext as sc


def newGuidStr():
    return str(uuid.uuid4())


class ChangeCurveDegreeTests(unittest.TestCase):
  def setUp(self):
    points = Rhino.Collections.Point3dList(5)
    points.Add(0, 0, 0)
    points.Add(0, 2, 0)
    points.Add(2, 3, 0)
    points.Add(4, 2, 0)
    points.Add(4, 0, 0)
    self.id = rs.AddCurve(points, 3)

  def test_FirstParamGuidNotObjReturnsNone(self):
    r = rs.ChangeCurveDegree(newGuidStr(), 4)
    self.assertTrue(r is None)
    
  def test_FirstParamValidGuidButGeoNotCurveReturnsNone(self):
    id = rs.AddPoint(g.Point3d.Origin)
    r = rs.ChangeCurveDegree(id, 4)
    self.assertTrue(r is None)

  def test_OutOfRangeDegreeReturnsFalse(self):
    max_nurbs_degree = 11
    self.assertTrue(not rs.ChangeCurveDegree(self.id, 0))
    self.assertTrue(not rs.ChangeCurveDegree(self.id, max_nurbs_degree + 1))
    
  def test_SameOrLowerDegreeReturnsFalse(self):
    self.assertTrue(not rs.ChangeCurveDegree(self.id, 3))
    self.assertTrue(not rs.ChangeCurveDegree(self.id, 2))

  def test_IncreaseByOne(self):
    self.assertTrue(rs.ChangeCurveDegree(self.id, 4))
    self.assertEqual(4, rs.coercecurve(self.id).ToNurbsCurve().Degree)

  def test_CurveIsALine(self):
    id = rs.AddLine(g.Point3d.Origin, (10,10,10))
    self.assertTrue(rs.ChangeCurveDegree(id, 3))
    self.assertTrue(3, rs.coercecurve(id).ToNurbsCurve().Degree)


suite = unittest.TestLoader().loadTestsFromTestCase(ChangeCurveDegreeTests)
unittestresult = unittest.TextTestRunner(verbosity=2).run(suite)