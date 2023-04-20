#NoEnv
#Persistent
#SingleInstance, Force
SetWorkingDir, %A_ScriptDir%
SetTitleMatchMode, 2
DetectHiddenWindows, On

Title = 09bfbb2a-5591-458a-89ea-240311669014
Menu, Tray, Icon, icon.ico
Run, cmd /c title %Title% && python "modswitcher.py",, Hide
WinWait, %Title%
WinGet, Id, ID, %Title%

OnExit("AHK_EXIT")
AHK_EXIT(ExitReason, ExitCode)
{
    global Id
    ControlSend, ahk_parent, ^c, ahk_id %Id%
}