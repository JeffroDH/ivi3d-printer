import csv, re, sys
feat={
 'sendPrintStartCMD':'print start','sendPrintPauseCMD':'print pause','sendPrintResumeCMD':'print resume','sendPrintStopCMD':'print stop',
 'disconnectToPC':'PC link / job control','stopPrinting':'print stop (cleanup)','PrintgcodefileFinish':'print finish','getOneLineFromFile':'file streaming','cachegcodeFromFile':'file streaming',
 'setTempReport':'status polling','setMessageReport':'status polling','closeTempReport':'status polling','getStatusFromThread':'status polling','sendGetPosCMD':'status polling','printComlpetedSet':'status polling','ZOffsetGet':'status parsing',
 'sendCheckFirmwareVersionCMD':'info query','sendCheckPrinterHeadMessagesCMD':'info query',
 'sendSetTargetTemperatureCMD':'temperature','coolDown':'temperature','sendSetBedTargetTemperatureCMD':'temperature','bedCoolDown':'temperature','preHeat':'temperature','waitHeadHeat':'temperature',
 'sendSetFanOnCMD':'fan','sendSetFanOffCMD':'fan',
 'setFeedrate':'speed/flow','setWorkSpeed':'speed/flow','setFlowrate':'speed/flow',
 'eplus':'filament / extruder','eminus':'filament / extruder','eAny':'filament / extruder','eAnySpeedOrLength':'filament / extruder',
 'goLeveling':'leveling/calibration','goCalibrate':'leveling/calibration','checkLevelingSensorInstalled':'leveling/calibration','goInstallLevelSensorPos':'leveling/calibration','goZOffsetPos':'leveling/calibration (Z offset)','SetZOffset':'leveling/calibration (Z offset)','sendGetOffsetCMD':'settings read','sendDeleteTuningDataCMD':'settings reset','backupFromFactoryData':'settings reset','saveChanged':'settings save','zfinetunePlus':'babystep','zfinetuneMinus':'babystep','zPrintingPlus':'babystep (while printing)','zPrintingMinus':'babystep (while printing)',
 'switchOnEndStop':'endstops','switchOffEndStop':'endstops',
 'goOrigin':'homing','printerAbnormalOrder':'error recovery motion','printerHeadAbnormalOrder':'error recovery motion',
 'sendCNCMoveOnCMD':'laser/CNC','sendLaserLightOnCMD':'laser pointer ("light")','sendLaserOrCNCOffCMD':'laser/CNC','setCNCorLaserStrength':'laser/CNC','runBoundaryAbsolutely':'laser/CNC framing','runBlockBoundary':'laser/CNC framing','laserBlockSetWorkOrign':'laser/CNC work origin','runFinetuneBlock':'laser focus test','goLaserFinetunePos':'laser focus test','setWorkOriginPoint':'laser/CNC work origin','goWorkOriginPoint':'laser/CNC work origin','setWorkCoordinate':'laser/CNC work origin',
 'ChangeToUpdateMode':'firmware update','jumpToBootloader':'firmware update','rxDataHandle':'reply parsing',
}
rows=[]
src = sys.argv[1] if len(sys.argv) > 1 else 'app_string_refs.tsv'
for l in open(src):
    fa,fn,ra,s=l.rstrip('\n').split('\t')
    if not re.match(r'(G|M|T)\d',s): continue
    short=fn.split('::')[-1]
    f=feat.get(short)
    if f is None:
        f='motion/jog' if re.match(r'[xyz](Any)?(plus|minus)|go(XY|Z)zeroPos|goAbsoluteZ|goXYZ',short,re.I) else 'other'
    note=''
    if short=='rxDataHandle': note='matched in replies, not sent'
    if short in('getOneLineFromFile','cachegcodeFromFile') and s in('M106','M107'): note='file lines scanned for fan state (UI isFanOn); passed through unchanged'
    if s in('M2411 S3',) and short in('cachegcodeFromFile','getOneLineFromFile','PrintgcodefileFinish'): note='appended at end of file (job end = stop, not S4)'
    if s=='M5' and short in('cachegcodeFromFile','getOneLineFromFile','PrintgcodefileFinish'): note='appended at end of file for Laser/CNC'
    rows.append([f,s.replace('\n','\\n'),fn,'0x'+fa.lstrip('0'),'0x'+ra.lstrip('0'),'C (literal ref resolved by tools/strrefs.py)',note])
rows.sort(key=lambda r:(r[0],r[2],r[1]))
with open('commands.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['feature','command_literal','function','function_addr','ref_addr','evidence','notes']); w.writerows(rows)
print(len(rows))
