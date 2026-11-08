import AppKit
import ApplicationServices
func attr(_ e: AXUIElement,_ key: String)->CFTypeRef? { var v:CFTypeRef?; AXUIElementCopyAttributeValue(e,key as CFString,&v); return v }
var result:[String:Any] = ["running":false,"accessible":AXIsProcessTrusted()]
if let app = NSWorkspace.shared.runningApplications.first(where: { ["com.apple.logic10","com.apple.mobilelogic"].contains($0.bundleIdentifier ?? "") }) {
 result["running"] = true; result["pid"] = app.processIdentifier
 let root = AXUIElementCreateApplication(app.processIdentifier)
 AXUIElementSetMessagingTimeout(root,0.3)
 if let wins = attr(root,"AXWindows") as? [AXUIElement] {
  let main = wins.first(where: {(attr($0,"AXMain") as? Bool) == true}) ?? wins.first
  if let w = main {
   if let doc = attr(w,"AXDocument") as? String, let url = URL(string:doc) { result["project"] = url.deletingPathExtension().lastPathComponent; result["filename"] = url.lastPathComponent }
   else if let title = attr(w,"AXTitle") as? String, !title.isEmpty { result["project"] = title }
   var count = 0; var playing = false; var recording = false; var foundPlay = false
   func walk(_ e:AXUIElement,_ depth:Int) {
    count += 1; if count > 1500 || depth > 14 { return }
    let role = attr(e,"AXRole") as? String ?? ""
    let label = (attr(e,"AXDescription") as? String ?? "").lowercased()
    let id = attr(e,"AXIdentifier") as? String ?? ""
    let active = (attr(e,"AXValue") as? NSNumber)?.intValue == 1
    if id == "controlBar/playButton" { foundPlay = true; playing = active }
    if id == "controlBar/recordButton" { recording = active }
    if role == "AXSlider" && ["tempo","andamento"].contains(label), let value = attr(e,"AXValue") as? NSNumber { result["bpm"] = value }
    if ["tracks header","cabeçalho de pistas"].contains(label) {
      let children = attr(e,"AXChildren") as? [AXUIElement] ?? []
      let tracks = children.filter { (attr($0,"AXDescription") as? String ?? "").range(of: "^(Track|Pista) [0-9]+", options:.regularExpression) != nil }
      if !tracks.isEmpty { result["tracks"] = tracks.count }
    }
    for c in (attr(e,"AXChildren") as? [AXUIElement] ?? []) { walk(c,depth+1) }
   }
   walk(w,0)
   if recording { result["transport"] = "Recording" } else if playing { result["transport"] = "Playing" } else if foundPlay { result["transport"] = "Stopped" }
  }
 }
}
let data = try! JSONSerialization.data(withJSONObject:result,options:[.sortedKeys]); print(String(data:data,encoding:.utf8)!)
