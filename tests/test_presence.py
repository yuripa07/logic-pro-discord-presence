import unittest, socket, threading, struct, json
import presence
class PresenceTests(unittest.TestCase):
 def setUp(self): self.p={'running':True,'project':'Example','transport':'Recording','bpm':120,'tracks':1}
 def test_recording(self):
  a=presence.activity(self.p,123)
  self.assertEqual(a['state'],'Recording · 120 BPM · 1 visible track')
  self.assertEqual(a['timestamps'],{'start':123})
  self.assertTrue(a['assets']['small_image'].endswith('/record.png'))
 def test_privacy(self):
  a=presence.activity(self.p,123,{'incognito':True})
  self.assertNotIn('Example',str(a));self.assertEqual(a['state'],'Incognito')
  a=presence.activity(self.p,123,{'project_mode':'hidden','timer':'off','transport':'hidden','show_tracks':False})
  for field in ['details','state','timestamps']:self.assertNotIn(field,a)
 def test_clear(self):
  self.assertIsNone(presence.activity({'running':False},123))
  self.assertIsNone(presence.activity(self.p,123,{'enabled':False}))
  self.assertEqual(presence.activity({'running':True},123)['state'],'Producing music')
 def test_fragmentation(self):
  a,b=socket.socketpair();a.settimeout(2);b.settimeout(2)
  raw=json.dumps({'evt':'READY'}).encode();frame=struct.pack('<II',1,len(raw))+raw
  def writer():
   for byte in frame:b.sendall(bytes([byte]))
  t=threading.Thread(target=writer);t.start()
  try:self.assertEqual(presence.receive(a),{'evt':'READY'})
  finally:t.join();a.close();b.close()
 def test_ping(self):
  a,b=socket.socketpair();a.settimeout(2);b.settimeout(2)
  presence.send(b,3,{'ping':1});presence.send(b,1,{'evt':'READY'})
  try:
   self.assertEqual(presence.receive(a),{'evt':'READY'})
   op,n=struct.unpack('<II',presence.exact(b,8));self.assertEqual(op,4)
   self.assertEqual(json.loads(presence.exact(b,n)),{'ping':1})
  finally:a.close();b.close()
