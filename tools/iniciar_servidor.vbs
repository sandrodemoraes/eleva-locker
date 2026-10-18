' Atalho na area de trabalho — abre CMD e mantem aberto (nao pisca e fecha)
Option Explicit

Dim fso, shell, toolsDir, projeto, bat, cmd

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

toolsDir = fso.GetParentFolderName(WScript.ScriptFullName)
projeto = fso.GetParentFolderName(toolsDir)
bat = projeto & "\iniciar_elevalocker.bat"
If Not fso.FileExists(bat) Then
    bat = toolsDir & "\iniciar_servidor.bat"
End If
cmd = Environ("ComSpec")

If Not fso.FileExists(bat) Then
    MsgBox "Arquivo nao encontrado:" & vbCrLf & bat, vbCritical, "ELEVA LOCKER"
    WScript.Quit 1
End If

If Not fso.FileExists(projeto & "\app.py") Then
    MsgBox "app.py nao encontrado em:" & vbCrLf & projeto, vbCritical, "ELEVA LOCKER"
    WScript.Quit 1
End If

shell.CurrentDirectory = projeto
' 1 = janela normal; /k = mantem CMD aberto apos erro
shell.Run """" & cmd & """ /k """ & bat & """", 1, False
