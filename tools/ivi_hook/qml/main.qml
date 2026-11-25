import QtQuick 2.9
import QtQuick.Window 2.2
import QtQuick.Controls 2.2
import "../qml"

Window {
    id: window
    visible: false
    width: 800
    height: 480
    color: "#FFFFFF"

    readonly property int headCheckRetryTime: 4

    property int hintMessage: 0
    property int windowContentType: 0
    property var homePage
    property var warningPage: Qt.createComponent("TTextDialog.qml").createObject(window)
    property string portName: ""
    property string printerHeadType: "N/A"
    property string printerDiameter: "N/A"
    property string failedShowStr: "Self-test failed, please contact After-sales Service."
    property string ipAdressStr: $globalFunction.WiFiIPAddress
    property bool isLinux: true
    property bool isSettingWizardPage: false
    property bool isCheckAgain: false
    property bool isControlClicked: false
    property bool isStatusClicked: false
    property bool isFilesClicked: false
    property bool isSettingsClicked: false
    property bool isNoHead: true
    property bool hasGoHome: false
    property bool copyDone: false
    property Component component: null;
    // Live Z-offset for the Adjust screen: this-print babystep and stored
    // M665 H (updated by IviHook). The Z position label stays start-relative
    // and does not include this offset.
    property real iviZBabystep: 0
    property real iviZHeight: -1

    signal closeFilePage();
    signal letWizardPageClose();
    signal closeAllPage();
    signal closeForbiddenPage();
    signal closeHomedDialog();

    onIpAdressStrChanged: {
        if(ipAdressStr !== "" ){//&& currentWiFiSSID !== ""){
            console.log("ip:", ipAdressStr);
        }
    }

//    TTextBtn{
//        id: copyBtn
//        visible: true
//        enabled: $globalFunction.usbInsert
//        width: 150
//        height: 50
//        radius: 25
//        color: enabled ? (containsPress ? "#BED1FF" : "#E7F0FF") : "#DDDDDD"
//        textColor: enabled ? "#193ADD" : "#666666"
//        text: "Copy"
//        textPixSize: 24
//        anchors.top: parent.top
//        anchors.topMargin: 50
//        anchors.right: parent.right
//        anchors.rightMargin: 325
//        onClicked: {
//            copyDone = $globalFunction.tempCopyFile();
//            console.log("copyDone:", copyDone);
//        }
//    }
//    Text{
//        anchors.top: copyBtn.top
//        anchors.topMargin: 8
//        anchors.left: copyBtn.right
//        anchors.leftMargin: 30
//        color: copyDone ? "green" : "red"
//        text: copyDone ? "YES" : "NO"
//        font.pixelSize: 24
//    }

    Rectangle{
        id:filesBtn
        width: 145
        height: 145
        anchors.top: parent.top
        anchors.topMargin: 137
        anchors.left: parent.left
        anchors.leftMargin: 50
        radius: 20
        color: filesArea.containsPress ? "#BED1FF" : "#E7F0FF"
        Image {
            id: filesImg
            height: 42
            width: 42
            source: "../img/files.png"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }
        MouseArea {
            id: filesArea
            anchors.fill: parent;
            onClicked: createFileSelectPage();
        }
    }
    Text {
        id: filesTxt
        text: "Files"
        width: 145
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        color: enabled ? (filesArea.containsPress ? "#193ADD" : "#333333") : "#DDDDDD"
        font.family: "SF Pro Display"
        font.pixelSize: 26
        anchors.top: filesBtn.bottom
        anchors.topMargin: 30
        anchors.horizontalCenter: filesBtn.horizontalCenter
    }
    function createFileSelectPage(){
        console.log("createFileSelectPage");
        var fileSelectPage = Qt.createComponent("showFolderPage.qml").createObject(window);
        fileSelectPage.visible = true;
        fileSelectPage.closeFromOutside.connect(closeFilePage);
        closeAllPage.connect(fileSelectPage.closeAllPageFromOutside);
    }
    function createCalibratePage(){
        var calPage;
        if(printerHeadType === "FDM")
        {
            calPage = Qt.createComponent("CalibrationFDM.qml").createObject(window);
            calPage.visible = true;
        }
        else if(printerHeadType == "Laser")
        {
            calPage = Qt.createComponent("CalibrationLaser.qml").createObject(window);
            calPage.visible = true;
        }
        else
        {
            var NoticeDialog = Qt.createComponent("TTextOneBtnDialog.qml").createObject(window);
            NoticeDialog.isWarningImg = false;
            NoticeDialog.warningMode = true;
            NoticeDialog.titleText = "Error";
            NoticeDialog.oneBtntext = "OK";
            NoticeDialog.contentText = "No FDM print head found, please install FDM print head to calibrate the printer."
            NoticeDialog.visible = true;
            NoticeDialog.oneBtnClicked.connect(NoticeDialog.destroy);
        }
    }

    Rectangle{
        id:controlBtn
        width: 145
        height: 145
        anchors.top: parent.top
        anchors.topMargin: 137
        anchors.left: parent.left
        anchors.leftMargin: 235
        radius: 20
        color: controlArea.containsPress ? "#BED1FF" : "#E7F0FF"
        Image {
            id: controlImg
            height: 42
            width: 42
            source: "../img/control.png"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }
        MouseArea {
            id: controlArea
            anchors.fill: parent;
            onClicked:
            {
                createControlPage();
            }
        }
    }
    Text {
        id: controlTxt
        text: "Control"
        width: 145
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        color: enabled ? (controlArea.containsPress ? "#193ADD" : "#333333") : "#DDDDDD"
        font.family: "SF Pro Display"
        font.pixelSize: 26
        anchors.top: controlBtn.bottom
        anchors.topMargin: 30
        anchors.horizontalCenter: controlBtn.horizontalCenter
    }
    Rectangle{
        id: headTypeLabel
        width: 150
        height: 30
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 36
        anchors.left: parent.left
        anchors.leftMargin: 50
        Image{
            id: rightImg
            visible: true
            width: Image.width
            height: Image.height
            anchors.top: parent.top
            anchors.left: parent.left
            source: {
                if (printerHeadType === "Laser")
                {
                    "../img/Laser.png"
                }
                else if(printerHeadType === "CNC")
                {
                    "../img/CNC.png"
                }
                else
                {
                    "../img/FDM.png"
                }
            }
        }
        Text{
            anchors.left: rightImg.right
            anchors.leftMargin: 11
            anchors.top: parent.top
            anchors.topMargin: 4
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            color: "#999999"
            text:
            {
                if (printerHeadType === "FDM")
                {
                    printerHeadType + " " + printerDiameter
                }
                else
                {
                    printerHeadType
                }
            }
            font.pointSize: 16
        }
    }
    Text{
        id: ipLabel
        anchors.left: parent.left
        anchors.leftMargin: 556
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 35
        text: "IP:"
        font.pointSize: 16
        color: "#999999"
    }
    Text{
        id: ipAddressTxt
        anchors.left: ipLabel.right
        anchors.leftMargin: 9
        anchors.top: ipLabel.top
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        font.pointSize: 16
        color: "#999999"
        text:{
            if(ipAdressStr !== "")
                ipAdressStr
            else
                "N/A"
        }
    }

    function  createControlPage(){
        var ControlTabPage;
        if (printerHeadType === "N/A" || printerHeadType === "FDM")
        {
            ControlTabPage = Qt.createComponent("ControlTabPageNew.qml").createObject(window);
        }
        else
        {
            console.log("Congtrol Laser or CNC page.");
            ControlTabPage = Qt.createComponent("ControlPageLaserCNC.qml").createObject(window);
        }
        ControlTabPage.printerHeadType = printerHeadType;
        ControlTabPage.visible = true;
        closeAllPage.connect(ControlTabPage.closeAllPageFromOutside);
    }

    Rectangle{
        id:calibrateBtn
        width: 145
        height: 145
        anchors.top: parent.top
        anchors.topMargin: 137
        anchors.left: parent.left
        anchors.leftMargin: 420
        radius: 20
        color: calibrateArea.containsPress ? "#BED1FF" : "#E7F0FF"
        Image {
            id: statusImg
            height: 42
            width: 42
            source: "../img/calibration.png"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }
        MouseArea {
            id: calibrateArea
            anchors.fill: parent;
            onClicked: createCalibratePage();
        }
    }
    Text {
        id: calibrateTxt
        text: "Calibration"
        width: 145
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        color: enabled ? (calibrateArea.containsPress ? "#193ADD" : "#333333") : "#DDDDDD"
        font.family: "SF Pro Display"
        font.pixelSize: 26
        anchors.top: calibrateBtn.bottom
        anchors.topMargin: 30
        anchors.horizontalCenter: calibrateBtn.horizontalCenter
    }
    Rectangle{
        id:settingBtn
        width: 145
        height: 145
        anchors.top: parent.top
        anchors.topMargin: 137
        anchors.left: parent.left
        anchors.leftMargin: 605
        radius: 20
        color: settingArea.containsPress ? "#BED1FF" : "#E7F0FF"
        Image {
            id: settingImg
            height: 42
            width: 42
            source: "../img/setting.png"
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }
        MouseArea {
            id: settingArea
            anchors.fill: parent;
            onClicked: createSettingPage();
        }
    }
    Text {
        id: settingTxt
        text: "Settings"
        width: 145
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        color: enabled ? (settingArea.containsPress ? "#193ADD" : "#333333") : "#DDDDDD"
        font.family: "SF Pro Display"
        font.pixelSize: 26
        anchors.top: settingBtn.bottom
        anchors.topMargin: 30
        anchors.horizontalCenter: settingBtn.horizontalCenter
    }
    function createSettingPage(){
        var SettingPage = Qt.createComponent("SettingsPage.qml").createObject(window);
        SettingPage.visible = true;
        SettingPage.z = 1;
        closeAllPage.connect(SettingPage.closeAllPageFromOutside);
    }
    BusyWindow{
        id: openMachineSelfTestWindow
        visible: false
    }
    IviHook {
        id: iviBridgeHook
    }
    Timer {
        id:successMessageTimer
        interval: 3000;
        running: false;
        repeat: false;
        onTriggered: {
            rectUnShowAnimate.running = true;
        }
    }
    Timer{
        id: testTimeoutTimer
        interval: 3 * 1000
        running: false
        repeat: true
        onTriggered: {
            if(headCheckRetryTime--)
            {
                $globalFunction.sendCheckPrinterHeadMessagesCMD();
            }
            else
            {
                $globalFunction.setNeedFinishSelfTest(false);
                openMachineSelfTestWindow.visible = false;
                materialAbnormalNotice.visible = false;
                testTimeoutTimer.stop();

                windowContentType = 1;
                createNoticeDialog();

                createAboutPage();

                window.visible = true;
            }
        }
    }
    Timer {
        id: gohometimeout
        interval: 20000
        repeat: false
        running: false;
        onTriggered: {
            console.log("gohometimeout ====================================================");
            gohometimeoutfunc();  // going home timeout
            gohometimeout.stop();
        }
    }
    Rectangle{
        id:successMessageRect
        z:1
        visible: false
        width: 440
        height: 76
        color: "#000000"
        radius: 10
        opacity: 0.7
        anchors.top: parent.top
        anchors.topMargin: 30
        anchors.left: parent.left
        anchors.leftMargin: 180
        NumberAnimation on opacity {
            id:rectShowAnimate
            running: successMessageRect.visible
            from: 0.0;
            to:0.7;
            duration: 500;
        }
        NumberAnimation on opacity {
            id:rectUnShowAnimate
            running: false
            from: 0.7;
            to:0.0;
            duration: 500;
            onRunningChanged: {
                if(running);
                else
                {
                    successMessageRect.visible = false;
                    letWizardPageClose();
                }
            }
        }
        Text {
            id: successMessageContent
            text: "Self-test Succeeded!"
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
            wrapMode: Text.Wrap
            color: "#FFFFFF"
            width: 440
            font.family: "SF Pro Display"
            font.pixelSize: 30
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
        }
    }
    WizardPageNew{
        id: openMachineWizardPage
        visible: false
        onWizardFinished:
        {
            showOPenMachineGuideSuccess();
        }
        onContactUsShow: window.contactUs();
    }
    function getPrintHeadMessages(HeadType,Diameter)
    {
        printerHeadType = HeadType;
        printerDiameter = Diameter;
        console.log(HeadType,printerHeadType);
        if(printerHeadType !== "N/A")
        {
            isNoHead = false;
        }
        else
        {
            isNoHead = true;
        }
    }
    function showScreenSleepingPage()
    {
        console.log("showScreenSleepingPage")
        sleepPage.visible = true;
    }
    function showOpenMachineSelfTestSuccess()
    {
        testTimeoutTimer.stop();
        openMachineSelfTestWindow.visible = false;
        window.visible = true;

        if (printerHeadType !== "N/A")
        {
            hintMessage = 1;
            successMessageRect.visible = true;
            rectUnShowAnimate.running = false;
            successMessageTimer.interval = 3000;
            successMessageTimer.start();
        }

        if(printerHeadType !== "N/A")
        {
            $globalFunction.setMessageReport();
            var showGuide = $globalFunction.getShowGuide();
            var needCalibration = $globalFunction.getNeedCalibration();
            if(showGuide)
            {
                console.log("run into wizardPageNew");
                var WizardPage = Qt.createComponent("WizardPageNew.qml").createObject(window);
            }
            else if(needCalibration)
            {
                console.log("show need calibration dialog.");
                var WizardNotice = Qt.createComponent("TTextOneBtnDialog.qml").createObject(window);
                WizardNotice.warningMode = false;
                WizardNotice.isWarningImg = false;
                WizardNotice.titleText = "Notice";
                WizardNotice.oneBtntext = "OK";
                WizardNotice.contentText = "The printer is not calibrated yet, and you can always run Wizard to calibrate the printer from Settings."
                WizardNotice.oneBtnClicked.connect(WizardNotice.destroy);
                WizardNotice.visible = true;
            }
        }
        else
        {
            showConnectWarning();
        }

        $globalFunction.sendCheckFirmwareVersionCMD();
    }
    function showOPenMachineGuideSuccess()
    {
        window.visible = true;
        hintMessage = 2;
        successMessageRect.visible = true;
        rectUnShowAnimate.running = false;
        successMessageTimer.interval = 3000;
        successMessageTimer.start();
        $globalFunction.setShowGuideAndChangeINIFile(false);
        //开机向导完成后，发送查询打印头消息，更新打印头状态
        $globalFunction.sendCheckPrinterHeadMessagesCMD();
    }
    function setMainpageVisible()
    {
        visible = true;
    }
    function showConnectWarning()
    {
        createAboutPage();
        var NoticeDialog = Qt.createComponent("TTextOneBtnDialog.qml").createObject(window);
        NoticeDialog.warningMode = true;
        NoticeDialog.isWarningImg = false;
        NoticeDialog.titleText = "Error";
        NoticeDialog.oneBtntext = "OK";
        NoticeDialog.contentText = "No toolhead found. Please make sure you installed the toolhead correctly. If you did,then there is something wrong with toolhead recognition. Please contact us."
        NoticeDialog.visible = true;
        NoticeDialog.oneBtnClicked.connect(NoticeDialog.destroy);
    }
    function goHomeNotice()
    {
        var NoticeDialog = Qt.createComponent("TTextOneBtnDialog.qml").createObject(window);
        NoticeDialog.warningMode = false;
        NoticeDialog.isWarningImg = false;
        NoticeDialog.titleText = "Notice";
        NoticeDialog.oneBtntext = "Going Home";
        NoticeDialog.contentText = "Motor is disabled, please go home to unlock the motor and obtain the X, Y, Z positions as the reference points."
        NoticeDialog.visible = true;
        NoticeDialog.oneBtnClicked.connect($globalFunction.goOrigin);
        closeHomedDialog.connect(NoticeDialog.destroy);
    }
    function createAboutPage()
    {
        var aboutUsPage = Qt.createComponent("AboutPage.qml").createObject(window);
        aboutUsPage.visible = true;
        aboutUsPage.z = 1;
        aboutUsPage.aboutHomeBtnClicked.connect(destroy);
    }
    function contactUs()
    {
        //about页面跳转
        $globalFunction.setShowGuideAndChangeINIFile(false);
    }
    function createNoticeDialog()
    {
        var NoticeDialog = Qt.createComponent("TTextOneBtnDialog.qml").createObject(window);

        if (windowContentType === 1)
        {
            NoticeDialog.isWarningImg = false;
            NoticeDialog.warningMode = true;
            NoticeDialog.titleText = "Error";
            NoticeDialog.oneBtntext = "OK";
            NoticeDialog.contentText = "No signal received from the controller. Please contact Aftersales Service."
            NoticeDialog.oneBtnClicked.connect(contactUs);
        }
        else if (windowContentType === 2)
        {
            NoticeDialog.isWarningImg = false;
            NoticeDialog.warningMode = false;
            NoticeDialog.titleText = "Notice";
            NoticeDialog.oneBtntext = "Going Home";
            NoticeDialog.contentText = "Motor is disabled, please go home to unlock the motor and obtain the X, Y, Z positions as the reference points."
            NoticeDialog.oneBtnClicked.connect(goingHome);
            closeHomedDialog.connect(NoticeDialog.destroy);
        }
        else if (windowContentType === 3)
        {
            NoticeDialog.isWarningImg = false;
            NoticeDialog.warningMode = true;
            NoticeDialog.titleText = "Error";
            NoticeDialog.oneBtntext = "OK";
            NoticeDialog.contentText = "Filament ran out, please change filament and then resume printing."
            NoticeDialog.oneBtnClicked.connect(NoticeDialog.destroy);
        }

        NoticeDialog.visible = true;
    }
    function goingHome()
    {
        homePage = Qt.createComponent("HomeWatingPage.qml").createObject(window);
        homePage.z = 5;
        $globalFunction.setIsHoming(true);
        $globalFunction.homingFinished.connect(homePage.destroy);
        $globalFunction.homingFinishedtimeoutstop.connect(goHomefinished);
        $globalFunction.goOrigin();
        gohometimeout.start();
    }
    function goHomefinished()
    {
        homePage.visible = false;
        gohometimeout.stop();
        $globalFunction.homingFinished.disconnect(goHomefinished);
        $globalFunction.homingFinishedtimeoutstop.disconnect(goHomefinished);
    }
    function createForbiddenPage(showForbiddenPage)
    {
        if(showForbiddenPage)
        {
            var NoticePage = Qt.createComponent("ForbiddenPage.qml").createObject(window);
            closeForbiddenPage.connect(NoticePage.destroy);
            NoticePage.z = 5;
        }
        else
        {
            closeForbiddenPage();
        }
    }
    function homedNoticeDialog(needGoHome)
    {
        if(needGoHome)
        {
            var goHomeNoticeDialog = Qt.createComponent("TTextOneBtnDialog.qml").createObject(window);
            goHomeNoticeDialog.warningMode = false;
            goHomeNoticeDialog.isWarningImg = false;
            goHomeNoticeDialog.titleText = "Notice";
            goHomeNoticeDialog.oneBtntext = "Going Home";
            goHomeNoticeDialog.contentText = "Motor is disabled, please go home to unlock the motor and obtain the X, Y, Z positions as the reference points."
            goHomeNoticeDialog.visible = true;
            goHomeNoticeDialog.oneBtnClicked.connect(goingHome);
            closeHomedDialog.connect(goHomeNoticeDialog.destroy);
        }
        else
        {
            closeHomedDialog();
        }
    }
    function motorProtectGoHome()
    {
        windowContentType = 2;
        createNoticeDialog();
    }
    function materialAbnormalNotice()
    {
        console.log("materialAbnormalNotice");
        windowContentType = 3;
        createNoticeDialog();
    }
    function gohometimeoutfunc()
    {
        var NoticeDialog = Qt.createComponent("TTextOneBtnDialog.qml").createObject(window);
        NoticeDialog.warningMode = true;
        NoticeDialog.isWarningImg = false;
        NoticeDialog.titleText = "Error";
        NoticeDialog.oneBtntext = "OK";
        NoticeDialog.contentText = "There are some problems with the printer, please repower on machine!"
        NoticeDialog.visible = true;
        NoticeDialog.oneBtnClicked.connect(NoticeDialog.destroy);
        goHomefinished();
    }
    function printhalterror()
    {
        var NoticeDialog = Qt.createComponent("TTextOneBtnDialog.qml").createObject(window);
        NoticeDialog.warningMode = true;
        NoticeDialog.isWarningImg = false;
        NoticeDialog.titleText = "Error";
        NoticeDialog.oneBtntext = "OK";
        NoticeDialog.contentText = "There are some problems with the printer, please repower on machine!"
        NoticeDialog.visible = true;
//        NoticeDialog.oneBtnClicked.connect(NoticeDialog.destroy);
    }

    Component.onCompleted: {
        $globalFunction.setPrintHeadType.connect(getPrintHeadMessages);
        $globalFunction.screenStartSleeping.connect(showScreenSleepingPage);
        $globalFunction.forbiddenScreen.connect(createForbiddenPage);
        $globalFunction.selfTestSuccess.connect(showOpenMachineSelfTestSuccess);

        //Abnormal handle.
        $globalFunction.motorAbnormalNotice.connect(motorProtectGoHome);
        $globalFunction.materialAbnormalNotice.connect(materialAbnormalNotice);
        $globalFunction.popupGoHomeDialog.connect(homedNoticeDialog);
        $globalFunction.printhalt.connect(printhalterror);

        $globalFunction.initOpenPort();

        openMachineSelfTestWindow.visible = true;
        window.visible = true;

        //开始自检
        $globalFunction.sendCheckPrinterHeadMessagesCMD();
        testTimeoutTimer.start();

        //开机自检以及向导相关,同时关闭wizardPage
        letWizardPageClose.connect(openMachineWizardPage.wizardPageClose);
    }
}
