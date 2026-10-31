import QtQuick
import QtTest
TestCase {
 name: "BatteryHover"
 width: 600; height: 100; visible: true
 when: windowShown
 QtObject {
  id: service
  property string connection: "connected"
  property var snapshot: ({status:{model:"Test buds",battery:{left:{percentage:80},right:{percentage:60}}},anc_modes:[]})
  property var lastResponse: null
  property int nextId: 1
  property int eqStatusCalls: 0
  property var customRequest: null
  property int reportRequests: 0
  property string reportPath: ""
  property var touchRequest: null
  property var holdCycleRequest: null
  property var findRequests: []
  property var findDeviceIds: []
  property var queuedRequests: []
  function request(command, params) {
   queuedRequests = queuedRequests.concat([{command:command, parameters:params}])
   if (command === "eq_status") return eqStatus()
   return nextId++
  }
  function setTouchControl(side, action, value) {
   touchRequest = {side:side, action:action, function:value}; return nextId++
  }
  function setHoldCycle(modes) {
   holdCycleRequest = modes.slice(); return nextId++
  }
  function findEarbuds(ringing, deviceId) {
   findRequests = findRequests.concat([ringing])
   findDeviceIds = findDeviceIds.concat([deviceId || ""])
   return nextId++
  }
  function eqStatus() { eqStatusCalls++; return nextId++ }
  function setEq(value) { return nextId++ }
  function setCustomEq(entryId, gains) {
   customRequest = ({entry_id: entryId, gains: gains}); return nextId++
  }
  function saveDiagnosticReport(path) { reportRequests++; reportPath = path; return nextId++ }
 }
 QtObject {
  id: host
  property bool vertical: false
  property int barSize: 26
  property color barForeground: "white"
  property color foreground: "white"
  property color background: "black"
  property string fontFamily: "sans-serif"
  property real panelAvailableWidth: 600
  property var shell: host
  function serviceFor(name) { return service }
  function showTooltip(item, text) {}
  function hideTooltip(item) {}
 }
 BarWidget { id: widget; bar: host; x: 200; y: 20; width: implicitWidth; height: implicitHeight }
 Component { id: anotherWidget; BarWidget { bar: host } }
 function init() {
  service.connection = "connected"
  service.snapshot = ({status:{model:"Test buds",battery:{left:{percentage:80},right:{percentage:60}}},
   anc_modes:[], capabilities:[], compatibility:"verified", session_connected:true})
  service.lastResponse = null
  service.eqStatusCalls = 0
  service.customRequest = null
  service.reportRequests = 0
  service.reportPath = ""
  service.touchRequest = null
  service.holdCycleRequest = null
  service.findRequests = []
  service.findDeviceIds = []
  service.queuedRequests = []
  widget.panelQueue = []
  host.panelAvailableWidth = 600
  widget.popupOpen = false
  widget.pendingRequestId = -1
  widget.pendingKind = ""
  widget.reportDetailsOpen = false
 }
 function touchSnapshot() {
  return {status:{model:"Nord", battery:{}}, anc_modes:[],
   capabilities:["touch_controls"], session_connected:true, compatibility:"verified",
   touch_controls:[
    {side:1,button:1,action:2,action_label:"Double tap",function:6,function_label:"Next track",
     writable:true,options:[{value:0,label:"None"},{value:5,label:"Previous track"},{value:6,label:"Next track"}]},
    {side:2,button:1,action:2,action_label:"Double tap",function:254,function_label:"Unknown (254)",
     writable:true,options:[{value:0,label:"None"},{value:6,label:"Next track"}]},
    {side:1,button:1,action:4,action_label:"Touch & hold",function:8,function_label:"Switch noise control",
     writable:false,options:[]}]}
 }
 function findSnapshot(state) {
  return {status:{model:"Nord",battery:{}},anc_modes:[],
   capabilities:["find_earbuds"],session_connected:true,compatibility:"verified",
   find_state:state,find_device_id:"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
 }
 function test_find_play_stop_follow_confirmed_state_and_handle_rejection() {
  service.snapshot = findSnapshot("stopped")
  widget.popupOpen = true
  var button = findChild(widget, "findEarbudsButton")
  verify(button !== null)
  var hint = findChild(widget, "findEarbudsHint")
  verify(hint.text.indexOf("Remove earbuds") !== -1)
  verify(button.text.indexOf("▶") !== -1)
  button.clicked()
  compare(service.findRequests, [true])
  verify(!widget.finding)
  verify(!button.enabled)
  service.snapshot = findSnapshot("ringing")
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,
   result:{acknowledged:true,state:"ringing"}}
  wait(0)
  verify(widget.finding && button.enabled)
  compare(button.text, "■ Stop")
  button.clicked()
  compare(service.findRequests, [true,false])
  service.snapshot = findSnapshot("unknown")
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,
   result:{acknowledged:false,state:"unknown",set_status:14}}
  wait(0)
  compare(button.text, "■ Stop")
  verify(widget.outcome.indexOf("not confirmed") !== -1)
  verify(hint.text.indexOf("unknown") !== -1)
  button.clicked()
  service.snapshot = findSnapshot("stopped")
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,
   result:{acknowledged:true,state:"stopped"}}
  wait(0)
  verify(!widget.finding)
  verify(button.text.indexOf("▶") !== -1)
 }
 function test_find_unknown_start_and_panel_close_keep_stop_available() {
  service.snapshot = findSnapshot("stopped")
  widget.popupOpen = true
  findChild(widget, "findEarbudsButton").clicked()
  service.snapshot = findSnapshot("unknown")
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,
   result:{acknowledged:false,state:"unknown",set_status:null}}
  wait(0)
  verify(widget.finding)
  widget.close()
  compare(service.findRequests, [true,false])
  verify(widget.finding) // closing cannot establish remote silence
  service.snapshot = findSnapshot("stopped")
  verify(!widget.finding)
 }
 function test_find_close_during_start_queues_stop_and_reopen_uses_shared_state() {
  service.snapshot = findSnapshot("stopped")
  widget.popupOpen = true
  findChild(widget, "findEarbudsButton").clicked()
  widget.close()
  compare(service.findRequests, [true,false])
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,
   result:{acknowledged:true,state:"ringing"}}
  service.snapshot = findSnapshot("ringing")
  widget.popupOpen = true
  compare(findChild(widget, "findEarbudsButton").text, "■ Stop")
  service.connection = "disconnected"
  verify(!findChild(widget, "findEarbudsButton").enabled)
 }
 function test_find_shared_state_expiry_and_destroyed_open_panel() {
  service.snapshot = findSnapshot("stopped")
  var other = createTemporaryObject(anotherWidget, this)
  verify(other !== null)
  widget.popupOpen = true
  other.popupOpen = true
  service.snapshot = findSnapshot("ringing")
  compare(findChild(widget, "findEarbudsButton").text, "■ Stop")
  compare(findChild(other, "findEarbudsButton").text, "■ Stop")
  // An open view going away must stop the same owned search.
  other.destroy()
  wait(0)
  compare(service.findRequests, [false])
  // Automatic stop arrives as a snapshot, without a UI command response.
  service.snapshot = findSnapshot("stopped")
  verify(!widget.finding)
  verify(findChild(widget, "findEarbudsButton").text.indexOf("▶") !== -1)
 }
 function test_find_close_after_device_switch_cancels_original_pending_start() {
  service.snapshot = findSnapshot("stopped")
  widget.popupOpen = true
  findChild(widget, "findEarbudsButton").clicked()
  var originalId = service.snapshot.find_device_id
  var next = findSnapshot("stopped")
  next.find_device_id = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  service.snapshot = next
  widget.close()
  compare(service.findRequests, [true,false])
  compare(service.findDeviceIds, [originalId,originalId])
 }
 function test_touch_controls_read_and_write_real_widget() {
  service.snapshot = touchSnapshot()
  widget.popupOpen = true
  compare(service.queuedRequests[0].command, "touch_controls")
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,result:{}}
  wait(0)
  findChild(widget, "touchControlsDisclosure").clicked()
  var left = findChild(widget, "touchSelector_1_2")
  var right = findChild(widget, "touchSelector_2_2")
  verify(left !== null)
  verify(right !== null)
  compare(left.currentText, "Next track")
  compare(left.count, 3)
  compare(right.currentText, "Unknown (254)")
  compare(findChild(widget, "touchSelector_1_4").visible, false)
  left.currentIndex = 1
  left.activated(1)
  compare(service.touchRequest.side, 1)
  compare(service.touchRequest.action, 2)
  compare(service.touchRequest.function, 5)
  compare(left.currentText, "Next track")  // display only confirmed state
  verify(!left.enabled)
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,result:{verified:false}}
  wait(0)
  verify(widget.outcome.indexOf("not confirmed") !== -1)
  verify(findChild(widget, "touchSelector_1_2").enabled)
  service.connection = "disconnected"
  wait(0)
  verify(!findChild(widget, "touchSelector_1_2").enabled)
 }
 function test_touch_controls_refresh_and_narrow_layout() {
  service.snapshot = touchSnapshot()
  host.panelAvailableWidth = 400
  widget.popupOpen = true
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,result:{}}
  wait(0)
  var section = findChild(widget, "touchControlsSection")
  verify(section.visible)
  findChild(widget, "touchControlsDisclosure").clicked()
  wait(0)
  var right = findChild(widget, "touchSide_2")
  var left = findChild(widget, "touchSide_1")
  verify(right.y > left.y)
  verify(right.x + right.width <= section.width)
  findChild(widget, "refreshTouchControls").clicked()
  compare(service.queuedRequests.length, 2)
  service.snapshot = {status:{battery:{}},capabilities:[],anc_modes:[]}
  wait(0)
  verify(!section.visible)
 }
 function test_hover() {
  mouseMove(widget, -100, 50)
  wait(220)
  var compact = widget.width
  verify(!widget.batteryExpanded)
  mouseMove(widget, compact / 2, 13)
  tryCompare(widget, "batteryExpanded", true)
  wait(220)
  verify(widget.width > compact + 50)
  var expanded = widget.width
  mouseMove(widget, expanded - 3, 13)
  verify(widget.batteryExpanded)
  mouseClick(widget, expanded - 3, 13)
  verify(widget.popupOpen)
  mouseMove(widget, -100, 50)
  wait(550)
  compare(widget.width, expanded)
  widget.close()
  wait(150)
  verify(widget.batteryExpanded)
  wait(450)
  compare(widget.width, compact)
  mouseMove(widget, compact / 2, 13)
  wait(220)
  mouseMove(widget, -100, 50)
  wait(150)
  verify(widget.batteryExpanded)
  mouseMove(widget, compact / 2, 13)
  wait(350)
  verify(widget.batteryExpanded)
  service.snapshot = {status:{battery:{case:{percentage:55}}},anc_modes:[]}
  wait(220)
  verify(widget.width > compact)
  verify(widget.width < expanded)
  service.connection = "disconnected"
  wait(220)
  verify(Math.abs(widget.width - compact) < 3)
  verify(!widget.batteryExpanded)
  service.connection = "connected"
  service.snapshot = {status:{battery:{}},anc_modes:[]}
  wait(220)
  compare(widget.width, compact)
 }
 function test_hold_cycle_is_shared_validated_and_applied_explicitly() {
  var state = touchSnapshot()
  state.capabilities.push("hold_cycle")
  state.hold_cycle = {modes:["anc","transparency"],min_selected:2,shared:true,writable:true,
   options:[{value:"anc",label:"Noise cancellation"},{value:"off",label:"Off"},
    {value:"transparency",label:"Transparency"}]}
  service.snapshot = state
  widget.popupOpen = true
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,result:{}}
  wait(0)
  var apply = findChild(widget, "applyHoldCycle")
  var anc = findChild(widget, "holdCycleOption_anc")
  var off = findChild(widget, "holdCycleOption_off")
  var transparency = findChild(widget, "holdCycleOption_transparency")
  verify(apply !== null)
  verify(!apply.visible)
  findChild(widget, "touchControlsDisclosure").clicked()
  wait(0)
  verify(anc.visible && off.visible && transparency.visible)
  verify(anc.checked)
  verify(!off.checked)
  verify(transparency.checked)
  verify(!apply.enabled)
  verify(findChild(widget, "touchSelector_1_4") === null)
  anc.clicked()
  verify(!apply.enabled)  // only one mode
  off.clicked()
  verify(apply.enabled)
  compare(service.holdCycleRequest, null)
  service.snapshot = JSON.parse(JSON.stringify(state))  // ordinary poll preserves draft
  wait(0)
  verify(!anc.checked && off.checked && transparency.checked)
  findChild(widget, "touchControlsDisclosure").clicked()
  findChild(widget, "touchControlsDisclosure").clicked()
  verify(!anc.checked && off.checked && transparency.checked)
  apply.clicked()
  compare(service.holdCycleRequest.join(","), "off,transparency")
  verify(!apply.enabled)
  verify(!anc.enabled)
  state.hold_cycle.modes = ["off","transparency"]
  service.snapshot = JSON.parse(JSON.stringify(state))
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,result:{verified:true}}
  wait(0)
  verify(!apply.enabled)
  verify(!anc.checked && off.checked && transparency.checked)
  anc.clicked()
  verify(apply.enabled)
  findChild(widget, "cancelHoldCycle").clicked()
  verify(!anc.checked)
  verify(!apply.enabled)
  anc.clicked()
  apply.clicked()
  // An ignored write restores the actual device state, never the draft.
  service.lastResponse = {request_id:widget.pendingRequestId,ok:true,result:{verified:false}}
  wait(0)
  verify(!anc.checked && off.checked && transparency.checked)
  verify(!apply.enabled)
  verify(widget.outcome.indexOf("not confirmed") !== -1)
  off.forceActiveFocus()
  verify(off.activeFocus)
  findChild(widget, "touchControlsDisclosure").clicked()
  verify(!off.activeFocus)
  findChild(widget, "touchControlsDisclosure").clicked()
  service.connection = "disconnected"
  wait(0)
  verify(!off.enabled)
  verify(!apply.enabled)
 }
 function test_disclosures_default_closed_independent_and_keep_edits() {
  var state = touchSnapshot()
  state.capabilities.push("eq", "bass_engine")
  state.custom_eq_write_verified = true
  state.eq = {current_id:7,current_name:"My curve",gain_step_db:1,
   presets:[{id:3,key:"balanced",name:"Balanced"}],
   custom_entries:[{eq_id:7,name:"My curve",min_gain_db:-6,max_gain_db:6,
    bands:[{frequency_hz:62,gain_db:3},{frequency_hz:250,gain_db:1}]}]}
  service.snapshot = state
  widget.popupOpen = true
  while (widget.pendingRequestId >= 0) {
   service.lastResponse = {request_id:widget.pendingRequestId,ok:true,result:{}}
  }
  wait(0)
  var customHeader = findChild(widget, "customEqDisclosure")
  var touchHeader = findChild(widget, "touchControlsDisclosure")
  var bands = findChild(widget, "customEqBands")
  var touch = findChild(widget, "touchSelector_1_2")
  verify(customHeader !== null)
  verify(touchHeader !== null)
  verify(!bands.visible)
  verify(!touch.visible)
  verify(findChild(widget, "currentEqLabel").visible)
  compare(findChild(widget, "currentEqLabel").text, "Current: My curve")
  var bass = findChild(widget, "bassWaveSection")
  verify(bass !== null)
  verify(customHeader.mapToItem(widget, 0, 0).y < bass.mapToItem(widget, 0, 0).y)
  compare(customHeader.mapToItem(widget, 0, 0).x, findChild(widget, "eqHeading").mapToItem(widget, 0, 0).x)
  compare(customHeader.width, findChild(widget, "eqHeading").width)
  compare(findChild(widget, "currentEqLabel").y, findChild(widget, "eqHeadingTitle").y)
  verify(findChild(widget, "currentEqLabel").x > findChild(widget, "eqHeadingTitle").x)
  var compactHeight = widget.panelHeight
  var fixedWidth = widget.contentWidth
  customHeader.clicked()
  wait(0)
  verify(bands.visible)
  verify(!touch.visible)
  tryVerify(function() { return widget.panelHeight > compactHeight })
  compare(widget.contentWidth, fixedWidth)
  var gain = findChild(widget, "customEqGain_62")
  gain.value = 5
  gain.forceActiveFocus()
  verify(gain.activeFocus)
  customHeader.clicked()
  wait(0)
  verify(!bands.visible)
  verify(!gain.activeFocus)
  tryCompare(widget, "panelHeight", compactHeight)
  touchHeader.clicked()
  wait(0)
  verify(touch.visible)
  verify(!bands.visible)
  compare(widget.contentWidth, fixedWidth)
  touch.forceActiveFocus()
  verify(touch.activeFocus)
  touchHeader.clicked()
  verify(!touch.activeFocus)
  customHeader.clicked()
  wait(0)
  compare(gain.value, 5)
  compare(service.customRequest, null)
  compare(service.touchRequest, null)
  touchHeader.clicked()
  gain.forceActiveFocus()
  verify(gain.activeFocus)
  widget.close()
  widget.popupOpen = true
  wait(0)
  verify(!bands.visible)
  verify(!touch.visible)
  verify(!gain.activeFocus)
  compare(widget.contentWidth, fixedWidth)
  service.snapshot = {status:{battery:{}},capabilities:[],anc_modes:[]}
  wait(0)
  verify(!customHeader.visible)
  verify(!touchHeader.visible)
 }
 function test_native_eq_panel_is_capability_driven() {
  service.snapshot = ({
   status:{model:"Test buds",battery:{left:{percentage:80},right:{percentage:60}}},
   anc_modes:[], capabilities:["eq"], session_connected:true,
   eq_write_verified:true, custom_eq_write_verified:true,
   eq:{current_id:4,current_name:"Custom",gain_step_db:1,
    presets:[{id:0,key:"balanced",name:"Balanced"}],
    custom_entries:[{eq_id:4,name:"Custom",min_gain_db:-6,max_gain_db:6,
     bands:[{frequency_hz:62,gain_db:3},{frequency_hz:250,gain_db:1}]}]}
  })
  widget.popupOpen = true
  tryCompare(service, "eqStatusCalls", 1)
  verify(widget.useTwoColumnLayout)
  compare(widget.eqPresets.length, 1)
  compare(widget.customEqEntries.length, 1)
  compare(widget.selectedCustom.bands.length, 2)
  verify(widget.reportActionShown)
  compare(widget.reportActionLabel, "Report a problem")
  verify(widget.panelHeight <= 510)
  service.lastResponse = ({request_id:widget.pendingRequestId,ok:true,result:service.snapshot.eq})
  wait(0)
  service.snapshot.eq.custom_entries.push({eq_id:5,name:"Custom1",min_gain_db:-6,max_gain_db:6,
   bands:[{frequency_hz:62,gain_db:0},{frequency_hz:250,gain_db:0}]})
  service.snapshot = JSON.parse(JSON.stringify(service.snapshot))
  wait(0)
  widget.selectCustomSlot(1)
  compare(widget.selectedCustom.eq_id, 5)
  service.snapshot = JSON.parse(JSON.stringify(service.snapshot))
  wait(0)
  compare(widget.selectedCustom.eq_id, 5)
  widget.applyCustomEq()
  verify(service.customRequest !== null)
  compare(service.customRequest.entry_id, 5)
  compare(service.customRequest.gains.join(","), "0,0")
  widget.pendingRequestId = -1
  widget.popupOpen = false
 }
 function test_panel_falls_back_when_width_is_narrow() {
  service.snapshot = ({status:{model:"Test buds",battery:{}}, anc_modes:["off","on"],
   capabilities:["eq"], session_connected:true, eq_write_verified:true,
   eq:{current_id:0,current_name:"Hans Zimmer Soundscape Tuning",presets:[],custom_entries:[]}})
  host.panelAvailableWidth = 559
  tryCompare(widget, "useTwoColumnLayout", false)
  host.panelAvailableWidth = 600
  tryCompare(widget, "useTwoColumnLayout", true)
 }
 function test_compatibility_notice_states_and_bounds() {
  service.snapshot = ({status:{model:"OnePlus Buds Pro",product_id:"060C14",battery:{}},
   compatibility:"verified", anc_modes:["off","on"], capabilities:[], session_connected:true})
  widget.popupOpen = true
  compare(widget.experimentalDevice, false)
  compare(widget.communityTestedDevice, false)
  verify(!widget.compatibilityNoticeShown)
  verify(widget.reportActionShown)
  compare(widget.reportActionLabel, "Report a problem")

  service.snapshot = ({status:{model:"OnePlus Buds Pro 2",product_id:"062014",battery:{}},
   compatibility:"verified", anc_modes:["off","on"], capabilities:[], session_connected:true})
  wait(0)
  compare(widget.experimentalDevice, false)
  verify(!widget.compatibilityNoticeShown)
  verify(widget.reportActionShown)
  compare(widget.reportActionLabel, "Report a problem")

  service.snapshot = ({status:{model:null,product_id:"A1B2C3",battery:{}},
   compatibility:"experimental", anc_modes:[], capabilities:[], session_connected:false})
  wait(0)
  verify(widget.experimentalDevice)
  verify(widget.compatibilityNoticeShown)
  verify(widget.reportActionShown)
  compare(widget.reportActionLabel, "Report compatibility")
  verify(widget.panelHeight <= 560)

  service.snapshot = ({status:{model:"Community model",product_id:"C0FFEE",battery:{}},
   compatibility:"community_tested", anc_modes:[], capabilities:[], session_connected:false})
  wait(0)
  verify(widget.communityTestedDevice)
  verify(widget.compatibilityNoticeShown)
  verify(widget.reportActionShown)
  compare(widget.reportActionLabel, "Report a problem")
  verify(widget.panelHeight <= 560)
  widget.popupOpen = false
 }

 function test_all_compatibility_states_share_report_workflow() {
  var states = ["verified", "community_tested", "experimental"]
  for (var i = 0; i < states.length; i++) {
   service.snapshot = ({status:{model:"Test buds",product_id:"TEST",battery:{}},
    compatibility:states[i], anc_modes:[], capabilities:[], session_connected:true})
   wait(0)
   widget.saveDiagnosticReport("file:///tmp/report.txt")
   compare(widget.pendingKind, "diagnostic_report")
   widget.pendingRequestId = -1
   widget.pendingKind = ""
  }
  compare(service.reportRequests, 3)
 }

 function test_report_filename_and_submission_outcomes() {
  service.snapshot = ({status:{model:"OnePlus Buds Pro 2",product_id:"062014",battery:{}},
   compatibility:"verified", anc_modes:[], capabilities:[], session_connected:true})
  widget.popupOpen = true
  widget.reportDetailsOpen = true
  widget.prepareReportFileDialog()
  verify(widget.proposedReportFilename.length > 0)
  verify(/^oneplus-buds-pro-2-report-[0-9]{4}-[0-9]{2}-[0-9]{2}\.txt$/.test(
   widget.proposedReportFilename))
  verify(widget.reportDialogSelectedFile.endsWith("/" + widget.proposedReportFilename))

  widget.saveDiagnosticReport("file:///tmp/oneplus-buds-pro-2-report-2026-09-16.txt")
  var successId = widget.pendingRequestId
  compare(service.reportRequests, 1)
  compare(service.reportPath, "file:///tmp/oneplus-buds-pro-2-report-2026-09-16.txt")
  service.lastResponse = ({request_id:successId,ok:true,
   result:{saved:true,filename:"oneplus-buds-pro-2-report-2026-09-16.txt"}})
  wait(0)
  verify(widget.reportSaved)
  verify(findChild(widget, "reportSavedGuidance").visible)
  compare(widget.savedReportFilename, "oneplus-buds-pro-2-report-2026-09-16.txt")
  compare(widget.savedReportLocation, "/tmp/oneplus-buds-pro-2-report-2026-09-16.txt")
  verify(widget.reportIssueUrl.indexOf("template=compatibility.md") !== -1)
  verify(widget.reportIssueUrl.indexOf("report=") === -1)

  widget.prepareReportFileDialog()
  widget.cancelDiagnosticReport()
  verify(!widget.reportSaved)
  verify(!findChild(widget, "reportSavedGuidance").visible)
  compare(widget.savedReportFilename, "")

  widget.saveDiagnosticReport("file:///tmp/failed-report.txt")
  var failureId = widget.pendingRequestId
  service.lastResponse = ({request_id:failureId,ok:false,
   error:{message:"Diagnostic report could not be saved"}})
  wait(0)
  verify(!widget.reportSaved)
  verify(!findChild(widget, "reportSavedGuidance").visible)
  compare(widget.savedReportFilename, "")
  widget.popupOpen = false
 }
}
