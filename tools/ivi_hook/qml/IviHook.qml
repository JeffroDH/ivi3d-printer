import QtQuick 2.9
import QtQuick.Window 2.3
import QtQml 2.2

// Always-live ivibridge hook, declared as a child of the main Window in
// main.qml. It is not created via Component.createObject, so a later
// BusyWindow root.destroy() after self-test cannot delete it.
//
// It is the single poller for start and mid-job requests (pause, resume,
// cancel, temp, speed, flow, zoffset). Auto-start comes from the request
// (bridge setting, default off): when true, skip the plate warning and run
// the stock RUN path.
Item {
    id: hook

    property bool calibrationLock: false
    property bool pollBusy: false
    property var appWindow: null
    property var gfn: $globalFunction
    property int lastId: 0
    property double lastPollAt: 0
    property string apiBase: "http://127.0.0.1:5001"
    property bool polling: false
    property int lastPrintStatus: -1

    function attach() {
        var w = Window.window;
        if (!w)
            return false;
        appWindow = w;
        return true;
    }

    function ack(id, ok, result) {
        var x = new XMLHttpRequest();
        x.open("GET", apiBase + "/api/ivi/a?id=" + id + "&ok=" + (ok ? 1 : 0) + "&result=" + encodeURIComponent(result));
        x.send();
    }

    function baseName(path) {
        var s = "" + path;
        var n = s.lastIndexOf("/");
        return n < 0 ? s : s.substring(n + 1);
    }

    function safePath(path) {
        var s = ("" + path).indexOf("file://") === 0 ? ("" + path).substring(7) : ("" + path);
        var n = baseName(s);
        return (s.indexOf("/userdata/WifiFile/") !== 0 || s.indexOf("..") !== -1 || !n || n[0] === ".") ? "" : s;
    }

    function start(id, file, auto) {
        if (calibrationLock) { ack(id, 0, "pc"); return; }
        var st = gfn.currentStatus;
        if (st === 1 || st === 2) { ack(id, 0, "busy"); return; }
        var w = appWindow ? appWindow : Window.window;
        if (w && w.isNoHead) { ack(id, 0, "nohead"); return; }
        var path = safePath(file);
        if (!path) { ack(id, 0, "badfile"); return; }
        var name = baseName(path);
        // Stock Make (WifiFileListPage) passes FolderListModel.filePath, a
        // local path like /userdata/WifiFile/name.gcode, not a file:// URL.
        // setSelectFileFullName() assigns that string and tail-calls
        // QFile::setFileName(); QFile::open() then uses the name as-is.
        gfn.setSelectFileFullName(path);
        gfn.setSelectedFileName(name);
        if (!gfn.checkGcodePrinterHeadType()) {
            gfn.setSelectFileFullName("");
            gfn.setSelectedFileName("N/A");
            ack(id, 0, "head");
            return;
        }
        hook.resetBaby();
        var S = Qt.createComponent("StatusPageNew.qml").createObject(w);
        if (!S) { ack(id, 0, "page"); return; }
        S.visible = true;
        if (auto) {
            if (!gfn.getGoOrignStatus())
                gfn.goOrigin();
            gfn.startPrinting();
            ack(id, 1, "started");
            return;
        }
        var D = Qt.createComponent("TTextDialog.qml").createObject(w);
        D.warningMode = true;
        D.isWarningImg = true;
        D.titleText = "Warning";
        D.contentText = (name.indexOf(".g") !== -1 || name.indexOf(".G") !== -1)
            ? "Please make sure the build plate is on the heated bed and it is clean & ready for printing. Continue?"
            : "Ready to process. Please make sure the material is properly fixed on the build plate. ";
        D.oneButtonMode = true;
        D.oneBtntext = "OK";
        D.oneBtnClicked.connect(D.destroy);
        D.visible = true;
        ack(id, 1, "opened");
    }

    function adjust(o) {
        if (o.nozzle != null && o.nozzle !== "")
            gfn.setTargetTemperature(parseInt(o.nozzle));
        if (o.bed != null && o.bed !== "")
            gfn.setBedTargetTemperature(parseInt(o.bed));
        var s = o.speed != null && o.speed !== "" ? o.speed : o.cmd === "speed" ? o.value : undefined;
        var f = o.flow != null && o.flow !== "" ? o.flow : o.cmd === "flow" ? o.value : undefined;
        if (s != null && s !== "")
            gfn.setWorkSpeed(parseInt(s));
        if (f != null && f !== "")
            gfn.setFlowrate("" + parseInt(f));
        // 0.1.19: Fan on/off, the same slots as the stock Status page Fan switch
        var fv = o.fan != null && o.fan !== "" ? o.fan : o.cmd === "fan" ? o.value : undefined;
        if (fv != null && fv !== "") {
            if (parseInt(fv) > 0)
                gfn.sendSetFanOnCMD();
            else
                gfn.sendSetFanOffCMD();
        }
        var z = o.zoffset != null && o.zoffset !== "" ? o.zoffset : o.cmd === "zoffset" ? o.value : undefined;
        if (z != null && z !== "") {
            var zs = ("" + z).replace(/^\+/, "");
            var dv = parseFloat(zs);
            if (zs.charAt(0) === "-")
                gfn.zfinetuneMinus(zs.substring(1));
            else if (dv > 0)
                gfn.zfinetunePlus(zs);
            if (!isNaN(dv))
                hook.addBaby(dv);
        }
    }

    function win() {
        return appWindow ? appWindow : Window.window;
    }

    function addBaby(delta) {
        var w = hook.win();
        if (!w)
            return;
        w.iviZBabystep = Math.round((w.iviZBabystep + delta) * 100) / 100;
    }

    function resetBaby() {
        var w = hook.win();
        if (w)
            w.iviZBabystep = 0;
    }

    function syncPrintState() {
        if (!gfn)
            return;
        var st = gfn.currentStatus;
        // Reset only when a new print starts, not on pause (2) → resume (1).
        if (st === 1 && lastPrintStatus !== 1 && lastPrintStatus !== 2)
            hook.resetBaby();
        lastPrintStatus = st;
    }

    function pullSettings() {
        var x = new XMLHttpRequest();
        x.onreadystatechange = function() {
            if (x.readyState !== 4 || x.status !== 200)
                return;
            var o;
            try { o = JSON.parse(x.responseText); } catch (e) { return; }
            var w = hook.win();
            if (!w || !o || !o.zoffset)
                return;
            var h = o.zoffset.height;
            if (h != null && h !== "") {
                var v = parseFloat(h);
                if (!isNaN(v))
                    w.iviZHeight = v;
            }
        };
        x.open("GET", apiBase + "/api/ivi/settings");
        x.send();
    }

    function pause(id, on) {
        var st = gfn.currentStatus;
        if (st !== 1 && st !== 2) { ack(id, 0, "no job"); return; }
        gfn.isPause(on);
        ack(id, 1, on ? "paused" : "resumed");
    }

    function dispatch(o) {
        var id = parseInt(o.id);
        var c = "" + o.cmd;
        if (!id || id === lastId)
            return;
        if (c === "start") {
            lastId = id;
            start(id, o.file, o.autostart);
        } else if (c === "pause") {
            lastId = id;
            pause(id, true);
        } else if (c === "resume") {
            lastId = id;
            pause(id, false);
        } else if (c === "toggle") {
            lastId = id;
            pause(id, gfn.currentStatus === 1);
        } else if (c === "cancel") {
            lastId = id;
            gfn.stopPrinting();
            ack(id, 1, "cancelled");
        } else if (c === "temp" || c === "speed" || c === "flow" || c === "adjust" || c === "zoffset" || c === "fan") {
            lastId = id;
            adjust(o);
            ack(id, 1, "set");
        }
    }

    function poll() {
        hook.syncPrintState();
        if (pollBusy && Date.now() - lastPollAt < 2000)
            return;
        var x = new XMLHttpRequest();
        pollBusy = true;
        lastPollAt = Date.now();
        x.onreadystatechange = function() {
            if (x.readyState !== 4)
                return;
            pollBusy = false;
            if (x.status !== 200)
                return;
            var o;
            try { o = JSON.parse(x.responseText); } catch (e) { return; }
            if (!o || !o.pending)
                return;
            dispatch(o);
        };
        x.open("GET", apiBase + "/api/ivi/r");
        x.send();
    }

    function startPolling() {
        if (polling)
            return;
        polling = true;
        pollTimer.running = true;
        settingsTimer.running = true;
        hook.pullSettings();
        console.log("qml hook poll start");
    }

    Timer {
        id: attachRetry
        interval: 800
        repeat: true
        running: true
        onTriggered: {
            if (hook.attach())
                running = false;
        }
    }

    // Delay the first poll so Window / $globalFunction are up. Attach is
    // retried independently so a late Window.window still gets stored.
    Timer {
        id: startDelay
        interval: 2000
        repeat: false
        running: true
        onTriggered: hook.startPolling()
    }

    Timer {
        id: pollTimer
        interval: 400
        repeat: true
        running: false
        onTriggered: hook.poll()
    }

    Timer {
        id: settingsTimer
        interval: 2000
        repeat: true
        running: false
        onTriggered: hook.pullSettings()
    }

    Component.onCompleted: {
        hook.attach();
        if (gfn && gfn.forbiddenScreen)
            gfn.forbiddenScreen.connect(function(on) { hook.calibrationLock = on; });
        console.log("qml hook attach " + (appWindow ? "ok" : "pending"));
    }
}
