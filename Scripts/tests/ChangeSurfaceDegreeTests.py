import unittest
import uuid

import Rhino
import Rhino.Geometry as g

import rhinoscriptsyntax as rs
import scriptcontext as sc


def newGuidStr():
    return str(uuid.uuid4())


class ChangeSurfaceDegreeTests(unittest.TestCase):
  def setUp(self):
    points = Rhino.Collections.Point3dList(5)
    points.Add(0, 0, 0)
    points.Add(0, 2, 1)
    points.Add(2, 3, 5)
    points.Add(4, 2, -6)
    self.id = rs.AddSrfPt(points)

  def test_FirstParamNotValidGuidReturnsNone(self):
    r = rs.ChangeSurfaceDegree(newGuidStr(), (4,4))
    self.assertTrue(r is None)
    
  def test_FirstParamValidGuidButGeoNotSrfReturnsNone(self):
    id = rs.AddPoint(g.Point3d.Origin)
    r = rs.ChangeSurfaceDegree(id, 4)
    self.assertTrue(r is None)

  def test_OutOfRangeDegreeReturnsFalse(self):
    max_nurbs_degree = 11
    self.assertTrue(not rs.ChangeSurfaceDegree(self.id, (0,0)))
    self.assertTrue(not rs.ChangeSurfaceDegree(self.id, (max_nurbs_degree + 1, max_nurbs_degree + 1)))
    
  def test_SameDegreeReturnsFalse(self):
    self.assertTrue(not rs.ChangeSurfaceDegree(self.id, (1,1)))

  def test_IncreaseByOne(self):
    self.assertTrue(rs.ChangeSurfaceDegree(self.id, (3,3)))
    d0 = rs.coercesurface(self.id).ToNurbsSurface().Degree(0)
    d1 = rs.coercesurface(self.id).ToNurbsSurface().Degree(1)
    self.assertEqual(3, d0)
    self.assertEqual(3, d1)


suite = unittest.TestLoader().loadTestsFromTestCase(ChangeSurfaceDegreeTests)
unittestresult = unittest.TextTestRunner(verbosity=2).run(suite)