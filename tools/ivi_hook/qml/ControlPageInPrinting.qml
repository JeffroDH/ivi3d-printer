import QtQuick 2.9
import QtQuick.Window 2.3
import QtQuick.Controls 2.2
import "../qml"

Rectangle {
    id:root
    visible: true
    width: 800
    height: 480
    color: "#FFFFFF"
    property int temperatureNum: 0
    property int lengthBtnChoosedNum: 3
    property string jogSpeedSelect: $globalFunction.flowrate
    property string jogLengthSelect: $globalFunction.materialStepLength + "mm"
    property string zoffsetVal: "0.05"

    function iviFmtBaby(v) {
        var x = Math.round((v || 0) * 100) / 100;
        var s = x.toFixed(2);
        if (x > 0)
            s = "+" + s;
        return s;
    }
    function iviOffsetLabel(baby, height) {
        var babyTxt = iviFmtBaby(baby) + " mm";
        if (height == null || height < 0)
            return "This print  " + babyTxt + "\nStored H  —";
        var eff = Math.round((height - baby) * 100) / 100;
        return "This print  " + babyTxt + "\nH  " + height.toFixed(2) + "  →  " + eff.toFixed(2);
    }
    function iviAddBaby(sign) {
        var w = Window.window;
        if (!w)
            return;
        var d = parseFloat(zoffsetVal) || 0;
        if (!d)
            return;
        w.iviZBabystep = Math.round((w.iviZBabystep + sign * d) * 100) / 100;
    }

    property int headTemperature: $globalFunction.Temperature
    property int headTargetTemperature: $globalFunction.targetTemperature
    property int bedTemperature: $globalFunction.bedTemperature
    property int bedTargetTemperature: $globalFunction.bedTargetTemperature

    property int printStatus: $globalFunction.currentStatus
    property bool isPrinting: $globalFunction.currentStatus === 1 ? true : false
    property bool isNoHead: false
    property bool materialBtnIsEnabled: true
    //默认为true，刚进入页面允许点击CNC或Laser开关
    property bool isCNCRunFinished: true
    property bool isCNCStopFinished: true
    signal cobackBtnclicked();
    signal coHomeBtnClicked();
    signal closeAllPageFromOutside();

    MouseArea{
        anchors.fill: parent
        onClicked: {}
    }

    Pagehead{
        id:controlHead
        z:1
        anchors.top: parent.top
        isMidLabelEnabled: false
        headText: "Adjust"
        rightMenuBtnEnabled: false
        onBackBtnClicked: {
            cobackBtnclicked();
            root.destroy();
        }
        onHomeBtnClicked: {
            coHomeBtnClicked();
            root.destroy();
        }
    }

    Rectangle{
        id: coordinateVal
        width: 544
        height: 52
        radius: 4
        border.width: 1
        border.color: "#DDDDDD"
        anchors.top: controlHead.bottom
        anchors.topMargin: 30
        anchors.left: parent.left
        anchors.leftMargin: 30
        Text {
            id: xPos
            text: $globalFunction.xValue === "" ? "X: " + "N/A" : "X: " + $globalFunction.xValue
            color: "#333333"
            font.family: "SF Pro Display"
            font.pixelSize: 20
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.top: parent.top
            anchors.topMargin: 14
            anchors.left: parent.left
            anchors.leftMargin: 21
        }
        Text {
            id: yPos
            text: $globalFunction.yValue === "" ? "Y: " + "N/A" :"Y: " + $globalFunction.yValue
            color: "#333333"
            font.family: "SF Pro Display"
            font.pixelSize: 20
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.top: parent.top
            anchors.topMargin: 14
            anchors.left: parent.left
            anchors.leftMargin: 228
        }
        Text {
            id: zPos
            text: $globalFunction.zValue === "" ? "Z: " + "N/A" :"Z: " + $globalFunction.zValue
            color: "#333333"
            font.family: "SF Pro Display"
            font.pixelSize: 20
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            anchors.top: parent.top
            anchors.topMargin: 14
            anchors.left: parent.left
            anchors.leftMargin: 429
        }
    }

    Text {
        id: headLabelTxt
        width: 52
        height: 21
        visible: true
        text: "Nozzle"
        font.family: "SF Pro Display"
        font.pixelSize: 16
        color: "#666666"
        anchors.top: ntempSelectRow.top
        anchors.left: coordinateVal.left
    }
    Text {
        id: headTempTxt
        width: 124
        height: 28
        visible: true
        text:  headTemperature + "℃/" + headTargetTemperature + "℃"
        font.family: "SF Pro Display"
        font.pixelSize: 22
        font.bold: true
        color: "#000000"
        anchors.top: headLabelTxt.bottom
        anchors.left: headLabelTxt.left
    }
    Row{
        id: ntempSelectRow
        enabled: true
        visible: true
        anchors.top: coordinateVal.bottom
        anchors.topMargin: 29
        anchors.left: parent.left
        anchors.leftMargin: 169
        Repeater {
            model: [210, 240, 270]
            Rectangle {
                width: 86
                height: 50
                color: modelData === headTargetTemperature ? "#BED1FF" : "#E7F0FF"//enabled ? (modelData === headTargetTemperature ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
                Text {
                    text: modelData + "℃"
                    font.family: "SF Pro Display"
                    font.pixelSize: 24
                    font.bold: modelData === headTargetTemperature ? true : false
                    color: enabled ? "#333333" : "#666666"
                    anchors.centerIn: parent
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        headTargetTemperature = modelData
                        $globalFunction.setTargetTemperature(headTargetTemperature)
                    }
                }
            }
        }
    }
    TTextBtn{
        id: ntempMinusBtn
        visible: true
        enabled: true
        width: 72
        height: 50
        color: enabled ? (containsPress ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
        textColor: enabled ? "#193ADD" : "#666666"
        text: "-"
        textPixSize: 24
        anchors.top: ntempSelectRow.top
        anchors.left: ntempSelectRow.right
        anchors.leftMargin: 2
        onClicked: {
            headTargetTemperature--;
            $globalFunction.setTargetTemperature(headTargetTemperature);
        }
        onLongPressedTrigger: {
            headTargetTemperature--;
            $globalFunction.setTargetTemperature(headTargetTemperature);
        }
    }
    TTextBtn{
        id: ntempPlusBtn
        visible: true
        enabled: true
        width: 72
        height: 50
        color: enabled ? (containsPress ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
        textColor: enabled ? "#193ADD" : "#666666"
        text: "+"
        textPixSize: 24
        anchors.top: ntempSelectRow.top
        anchors.left: ntempMinusBtn.right
        anchors.leftMargin: 2
        onClicked: {
            headTargetTemperature++;
            $globalFunction.setTargetTemperature(headTargetTemperature);
        }
        onLongPressedTrigger:
        {
            headTargetTemperature++;
            $globalFunction.setTargetTemperature(headTargetTemperature);
        }
    }

    onHeadTargetTemperatureChanged: {
        if(headTargetTemperature === 280)
        {
            ntempMinusBtn.enabled = true;
            ntempPlusBtn.enabled = false;
            $globalFunction.setTargetTemperature(headTargetTemperature);
        }
        else if(headTargetTemperature === 0)
        {
            ntempMinusBtn.enabled = false;
            ntempPlusBtn.enabled = true;
            $globalFunction.setTargetTemperature(headTargetTemperature);
        }
        else
        {
            ntempMinusBtn.enabled = true;
            ntempPlusBtn.enabled = true;
        }
    }

    Text {
        id: bedLabelTxt
        width: 34
        height: 21
        text: "Bed"
        font.family: "SF Pro Display"
        font.pixelSize: 16
        color: "#666666"
        anchors.top: btempSelectRow.top
        anchors.left: coordinateVal.left
    }
    Text {
        id: bedTempTxt
        width: 105
        height: 28
        text: {
            bedTemperature + "℃/" + bedTargetTemperature + "℃"
        }
        font.family: "SF Pro Display"
        font.pixelSize: 22
        font.bold: true
        color: "#333333"
        anchors.top: bedLabelTxt.bottom
        anchors.left: bedLabelTxt.left
    }
    Row{
        id: btempSelectRow
        anchors.top: ntempSelectRow.bottom
        anchors.topMargin: 25
        anchors.left: ntempSelectRow.left
        Repeater {
            model: [60, 80, 100]
            Rectangle {
                width: 86
                height: 50
                color: modelData === bedTargetTemperature ? "#BED1FF" : "#E7F0FF"
                Text {
                    text: modelData + "℃"
                    font.family: "SF Pro Display"
                    font.pixelSize: 24
                    font.bold: modelData === bedTargetTemperature ? true : false
                    color: "#333333"
                    anchors.centerIn: parent
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        bedTargetTemperature = modelData;
                        $globalFunction.setBedTargetTemperature(bedTargetTemperature);
                    }
                }
            }
        }
    }

    TTextBtn{
        id: btempMinusBtn
        visible: true
        enabled: (bedTargetTemperature === 0) ? false : true
        width: 72
        height: 50
        color: enabled ? (containsPress ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
        textColor: enabled ? "#193ADD" : "#666666"
        text: "-"
        textPixSize: 24
        anchors.top: btempSelectRow.top
        anchors.left: btempSelectRow.right
        anchors.leftMargin: 2
        onClicked: {
            bedTargetTemperature--;
            $globalFunction.setBedTargetTemperature(bedTargetTemperature);
        }
        onLongPressedTrigger:{
            bedTargetTemperature--;
            $globalFunction.setBedTargetTemperature(bedTargetTemperature);
        }
    }
    TTextBtn{
        id: btempPlusBtn
        visible: true
        enabled: true
        width: 72
        height: 50
        color: enabled ? (containsPress ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
        textColor: enabled ? "#193ADD" : "#666666"
        text: "+"
        textPixSize: 24
        anchors.top: btempSelectRow.top
        anchors.left: btempMinusBtn.right
        anchors.leftMargin: 2
        onClicked: {
            bedTargetTemperature++;
            $globalFunction.setBedTargetTemperature(bedTargetTemperature);
        }
        onLongPressedTrigger:{
            bedTargetTemperature++;
            $globalFunction.setBedTargetTemperature(bedTargetTemperature);
        }
    }
    onBedTargetTemperatureChanged: {
        if(bedTargetTemperature === 130)
        {
            btempPlusBtn.enabled = false;
            btempMinusBtn.enabled = true;
            $globalFunction.setBedTargetTemperature(bedTargetTemperature);
        }
        else if(bedTargetTemperature === 0)
        {
            btempPlusBtn.enabled = true;
            btempMinusBtn.enabled = false;
            $globalFunction.setBedTargetTemperature(bedTargetTemperature);
        }
        else
        {
            btempMinusBtn.enabled = true;
            btempPlusBtn.enabled = true;
        }
    }

    Text{
        id: speedTxt
        text: "Jog Speed\n(mm/min)"
        font.pixelSize: 16
        textFormat: Text.RichText
        width: 90
        height: 48
        wrapMode: Text.Wrap
        color: "#666666"
        font.family: "SF Pro Display"
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignLeft
        anchors.top: speedOption.top
        anchors.topMargin: 1
        anchors.left: coordinateVal.left
    }
    Row{
        id: speedOption
        enabled: $globalFunction.currentStatus !== 1 ? true : false
        visible: true
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 104
        anchors.left: ntempSelectRow.left
        Repeater {
            model: ["100", "200", "500", "1000"]
            Rectangle {
                width: 75
                height: 50
                color: enabled ? (modelData === jogSpeedSelect ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
                Text {
                    text: modelData
                    font.family: "SF Pro Display"
                    font.pixelSize: 24
                    font.bold: modelData === jogSpeedSelect ? true : false
                    color: "#333333"
                    anchors.centerIn: parent
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        jogSpeedSelect = modelData
                        $globalFunction.flowrate = jogSpeedSelect
                    }
                }
            }
        }
    }

    Text {
        id: distanceTxt
        text: "Jog Distance\n(mm)"
        verticalAlignment: Text.AlignVCenter
        textFormat: Text.RichText
        width: 109
        height: 48
        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        color: "#666666"
        font.family: "SF Pro Display"
        font.pixelSize: 16
        horizontalAlignment: Text.AlignLeft
        anchors.top: distanceOption.top
        anchors.topMargin: 1
        anchors.left: speedTxt.left
    }
    Row{
        id: distanceOption
        enabled: $globalFunction.currentStatus !== 1 ? true : false
        visible: true
        anchors.top: speedOption.bottom
        anchors.topMargin: 24
        anchors.left: speedOption.left
        Repeater {
            model: ["10", "20", "50", "100"]
            Rectangle {
                width: 75
                height: 50
                color: enabled ? (modelData === jogLengthSelect ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
                Text {
                    text: modelData
                    font.family: "SF Pro Display"
                    font.pixelSize: 24
                    font.bold: modelData === jogLengthSelect ? true : false
                    color: "#333333"
                    anchors.centerIn: parent
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        jogLengthSelect = modelData;
                        $globalFunction.materialStepLength = jogLengthSelect;
                    }
                }
            }
        }
    }

    TTextBtn{
        id: movePlusBtn
        visible: true
        enabled: {
             if(distanceOption.enabled)
             {
                 if($globalFunction.Temperature < 170)
                 {
                     false
                 }
                 else
                 {
                     true
                 }
             }
             else
                 false
        }
        width: 91
        height: 50
        radius: 25
        color: enabled ? (containsPress ? "#3E61EA" : "#193ADD") : "#DDDDDD"
        textColor: "#FFFFFF"
        text: "Extrude"
        textPixSize: 20
        anchors.top: speedOption.top
        anchors.right: coordinateVal.right
        onClicked: {
            $globalFunction.eplus();
        }
    }
    TTextBtn{
        id: moveMinusBtn
        visible: true
        enabled: {
            if(distanceOption.enabled)
            {
                if($globalFunction.Temperature < 170)
                {
                    false
                }
                else
                {
                    true
                }
            }
            else
                false
        }
        width: 91
        height: 50
        radius: 25
        color: enabled ? (containsPress ? "#3E61EA" : "#193ADD") : "#DDDDDD"
        textColor: "#FFFFFF"
        text: "Retract"
        textPixSize: 20
        anchors.top: movePlusBtn.bottom
        anchors.topMargin: 24
        anchors.right: coordinateVal.right
        onClicked: {
            $globalFunction.eminus();
        }
    }

    Text {
        id: zAxisTxt
        text: "Z Offset\nDistance(mm)"
        verticalAlignment: Text.AlignVCenter
        textFormat: Text.RichText
        width: 109
        height: 48
        wrapMode: Text.WrapAtWordBoundaryOrAnywhere
        color: "#666666"
        font.family: "SF Pro Display"
        font.pixelSize: 16
        horizontalAlignment: Text.AlignLeft
        anchors.top: controlHead.bottom
        anchors.topMargin: 42
        anchors.left: finetuneOption.left
    }
    Text {
        id: zOffsetReadout
        width: 128
        wrapMode: Text.WordWrap
        color: "#193ADD"
        font.family: "SF Pro Display"
        font.pixelSize: 16
        font.bold: true
        horizontalAlignment: Text.AlignLeft
        text: iviOffsetLabel(Window.window ? Window.window.iviZBabystep : 0,
                             Window.window ? Window.window.iviZHeight : -1)
        anchors.top: zAxisTxt.bottom
        anchors.topMargin: 6
        anchors.right: finetuneOption.left
        anchors.rightMargin: 12
    }
    Column{
        id: finetuneOption
        enabled: $globalFunction.currentStatus === 1 ? true : false//currentStatus == Printing => enable
        visible: true
        anchors.top: controlHead.bottom
        anchors.topMargin: 99
        anchors.right: parent.right
        anchors.rightMargin: 43
        Repeater {
            model: ["0.01", "0.02", "0.05"]
            Rectangle {
                width: 120
                height: 50
                color: enabled ? (modelData === zoffsetVal ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
                Text {
                    text: modelData
                    font.family: "SF Pro Display"
                    font.pixelSize: 24
                    font.bold: modelData === zoffsetVal ? true : false
                    color: "#333333"
                    anchors.centerIn: parent
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        zoffsetVal = modelData
                    }
                }
            }
        }
    }
    TTextBtn{
        id :zPlusBtn
        enabled: $globalFunction.currentStatus === 1 ? true : false
        width: 120
        height: 60
        radius: 10
        color: enabled ? (containsPress ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
        textColor: enabled ? "#193ADD" : "#333333"
        text: "Z+"
        textPixSize: 24
        anchors.top: finetuneOption.bottom
        anchors.topMargin: 9
        anchors.left: finetuneOption.left
        onClicked: {
            $globalFunction.zfinetunePlus(zoffsetVal);
            iviAddBaby(1);
        }
    }
    TTextBtn{
        id :zMinusBtn
        enabled: $globalFunction.currentStatus === 1 ? true : false//printStatus === 1 ? true : false
        width: 120
        height: 60
        radius: 10
        color: enabled ? (containsPress ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
        textColor: enabled ? "#193ADD" : "#333333"
        text: "Z-"
        textPixSize: 24
        anchors.top: zPlusBtn.bottom
        anchors.topMargin: 10
        anchors.left: finetuneOption.left
        onClicked: {
            $globalFunction.zfinetuneMinus(zoffsetVal);
            iviAddBaby(-1);
        }
    }

    Component.onCompleted:
    {
        $globalFunction.checkPrintHeadMessages();
        closeAllPageFromOutside.connect(controlHead.homeBtnClicked);
    }
}
