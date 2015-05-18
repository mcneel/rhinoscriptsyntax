import rhinoscriptsyntax as rs
import scriptcontext as sc
import unittest
import uuid
import Rhino.Geometry as g

def uniquestr():
    return str(uuid.uuid4())

class AddPatchTests(unittest.TestCase):
  def setUp(self):
    pass

  def test_InvalidArgumentsReturnsNone(self):
    self.assertTrue(rs.AddPatch(uniquestr(), uniquestr()) == None)
    
  def test_SimpleWithSurfaceAndDefaults(self):
    id = rs.AddCircle((0,0,0), 20)
    srf_id = rs.AddPlanarSrf(id)
    pt_ids = rs.AddPoints([(-20,0,0), (0,20,0), (20,0,0)])
    id = rs.AddPatch(pt_ids, srf_id)
    brep = rs.coercebrep(id, True)
    self.assertTrue(brep.IsSurface)

  def test_SimpleWithUVSpansAndDefaults(self):
    pt_ids = rs.AddPoints([(-20,0,0), (0,20,0), (20,0,0)])
    id = rs.AddPatch(pt_ids, (10,10))
    brep = rs.coercebrep(id, True)
    self.assertTrue(brep.IsSurface)

suite = unittest.TestLoader().loadTestsFromTestCase(AddPatchTests)
unittestresult = unittest.TextTestRunner(verbosity=2).run(suite)