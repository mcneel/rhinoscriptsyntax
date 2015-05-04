import rhinoscriptsyntax as rs
import scriptcontext as sc
import unittest
import Rhino.Geometry as g

class PointArrayBoundingBoxTests(unittest.TestCase):
  def test_FirstParamNotPointsReturnsNone(self):
    r = rs.PointArrayBoundingBox("notpoints")
    self.assertTrue(r is None)

  def test_2ndParamNotPlaneOrViewReturnsNone(self):
    r = rs.PointArrayBoundingBox([(0,0,0), (5,5,5)], "notplaneorview")
    self.assertTrue(r is None)

  def test_SimpleWorldCoordsBBox(self):
    corners = rs.PointArrayBoundingBox([(0,0,0), (5,5,5)])
    self.assertTrue(any(pt.X == 0 and pt.Y == 0 and pt.Z == 0) for pt in corners)
    self.assertTrue(any(pt.X == 5 and pt.Y == 5 and pt.Z == 5) for pt in corners)

  def test_SimpleCustomPlaneBBox(self):
    plane = g.Plane(g.Point3d.Origin, g.Vector3d(1,1,0))
    points = [(-3,-3,-3), (4,4,4)]
    corners = rs.PointArrayBoundingBox(points, plane)
    self.assertTrue(any(pt.EpsilonEquals(g.Point3d(7.5, 0.5, 4), 0.001) for pt in corners))
    self.assertTrue(any(pt.EpsilonEquals(g.Point3d(-6.5, 0.5, -3), 0.001) for pt in corners))

suite = unittest.TestLoader().loadTestsFromTestCase(PointArrayBoundingBoxTests)
unittestresult = unittest.TextTestRunner(verbosity=2).run(suite)
