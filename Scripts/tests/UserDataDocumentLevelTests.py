import rhinoscriptsyntax as rs
import scriptcontext as sc
import unittest
import uuid
import Rhino.Geometry as g

def uniquestr():
    return str(uuid.uuid4())
def sec_ent_val():
    return uniquestr(), uniquestr(), uniquestr()
    
class UserDataDocumentLevelTests(unittest.TestCase):
  def setUp(self):
    rs.DeleteDocumentData()
    # there's no DeleteDocumentUserText()
    keys = rs.GetDocumentUserText()
    if keys:
      for k in keys:
        rs.SetDocumentUserText(k)

  # GetDocumentUserText
  def test_GetDocumentUserTextReturnsNoneForBadKey(self):
    self.assertTrue(rs.GetDocumentUserText(uniquestr()) == None)
  def test_GetDocumentUserTextReturnsNoneForEmptyList(self):
    self.assertTrue(rs.GetDocumentUserText() == None)
  def test_GetDocumentUserText_Typical(self):
      _, k, v = sec_ent_val()
      rs.SetDocumentUserText(k, v)
      self.assertEqual(v, rs.GetDocumentUserText(k))
  def test_GetDocumentUserTextWithNoArgsIgnoresDocumentData(self):
      s,k,v = sec_ent_val()
      rs.SetDocumentData(s,k,v)
      rs.SetDocumentUserText(k,v)
      _,k,v = sec_ent_val()
      rs.SetDocumentUserText(k,v)
      self.assertTrue(not any("\\" in k for k in rs.GetDocumentUserText()))
      self.assertEqual(2, rs.GetDocumentUserText().Count)
    
  # SetDocumentUserText
  def test_SetDocumentUserText_Typical(self):
    _,k,v = sec_ent_val()
    self.assertTrue(rs.SetDocumentUserText(k, v))
    self.assertEqual(v, rs.GetDocumentUserText(k))
  def test_SetDocumentUserTextDoesNotAcceptBackSlashesInKey(self):
    s, e, v = sec_ent_val()
    self.assertRaises(ValueError, rs.SetDocumentUserText, s + "\\" + e, v)

  # GetDocumentData
  def test_GetDocumentDataReturnsNoneForBadSectionOrEntry(self):
    s, e, v = sec_ent_val()
    self.assertTrue(rs.GetDocumentData(s) == None)
    rs.SetDocumentData(s, e, v)
    self.assertTrue(rs.GetDocumentData(s, uniquestr()) == None)
  def test_GetDocumentDataNoArgsReturnsSectionNames(self):
    s,e,v = sec_ent_val()
    rs.SetDocumentData(s, e, v)
    _,e,v = sec_ent_val()
    rs.SetDocumentData(s, e, v)
    self.assertEqual([s], rs.GetDocumentData())
  def test_GetDocumentDataSectionNameReturnsEntryNames(self):
    s,e1,v = sec_ent_val()
    rs.SetDocumentData(s, e1, v)
    _,e2,v = sec_ent_val()
    rs.SetDocumentData(s, e2, v)
    self.assertEqual([e1,e2], rs.GetDocumentData(s))
  def test_GetDocumentData_Typical(self):
    s,e,v = sec_ent_val()
    rs.SetDocumentData(s,e,v)
    self.assertEqual(v, rs.GetDocumentData(s,e))
    
  # SetDocumentData
  def test_SetDocumentDataReturnsNoneForNew(self):
    section, entry, value = sec_ent_val()
    self.assertTrue(rs.SetDocumentData(section, entry, value) == None)

  # IsDocument(Data|UserText)
  def test_IsDocumentDataIgnoresUserText(self):
    _,k,v = sec_ent_val()
    rs.SetDocumentUserText(k,v)
    self.assertTrue(rs.IsDocumentData() == False)
  def test_DocumentDataCountIgnoresUserText(self):
    _,k,v = sec_ent_val()
    rs.SetDocumentUserText(k,v)
    self.assertEqual(0, rs.DocumentDataCount())
    s,e,v = sec_ent_val()
    rs.SetDocumentData(s,e,v)
    s,e,v = sec_ent_val()
    rs.SetDocumentData(s,e,v)
    self.assertEqual(2, rs.DocumentDataCount())
  def test_IsDocumentUserTextIgnoresDocumentData(self):
    s,e,v = sec_ent_val()
    rs.SetDocumentData(s,e,v)
    s,e,v = sec_ent_val()
    rs.SetDocumentData(s,e,v)
    self.assertEqual(0, rs.DocumentUserTextCount())
    self.assertTrue(rs.IsDocumentUserText() == False)
  def test_DocumentUserTextCountIgnoresDocumentData(self):
    s,e,v = sec_ent_val()
    rs.SetDocumentData(s,e,v)
    self.assertEqual(0, rs.DocumentUserTextCount())
    _,k,v = sec_ent_val()
    rs.SetDocumentUserText(k,v)
    _,k,v = sec_ent_val()
    rs.SetDocumentUserText(k,v)
    self.assertEqual(2, rs.DocumentUserTextCount())
    
  # DeleteDocumentData
  def test_DeleteDocumentDataFailsOnEntryWithNoneSection(self):
      s, e, v = sec_ent_val()
      rs.SetDocumentData(s, e, v)
      self.assertRaises(TypeError, rs.DeleteDocumentData, None, e)
  def test_DeleteDocumentData_not_delete_DocumentUserText(self):
      s, e, v = sec_ent_val()
      rs.SetDocumentData(s, e, v)
      _, k, v = sec_ent_val()
      rs.SetDocumentUserText(k, v)
      rs.DeleteDocumentData()
      self.assertEqual(v, rs.GetDocumentUserText(k))
      
suite = unittest.TestLoader().loadTestsFromTestCase(UserDataDocumentLevelTests)
unittestresult = unittest.TextTestRunner(verbosity=2).run(suite)
