Option Explicit

Dim fso, shell, scriptDir, toolsDir, projeto, bat, desktop, startup, ok

Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
toolsDir = scriptDir
projeto = fso.GetParentFolderName(toolsDir)

If fso.FolderExists("C:\ElevaLocker") And fso.FileExists("C:\ElevaLocker\app.py") Then
    projeto = "C:\ElevaLocker"
End If

bat = projeto & "\iniciar_elevalocker.bat"
If Not fso.FileExists(bat) Then
    bat = projeto & "\tools\iniciar_servidor.bat"
End If

If Not fso.FileExists(bat) Then
    MsgBox "Nao achei iniciar_elevalocker.bat em:" & vbCrLf & projeto, vbCritical, "ELEVA LOCKER"
    WScript.Quit 1
End If

On Error Resume Next

desktop = shell.SpecialFolders("Desktop")
Call CriarAtalho(desktop & "\ELEVA LOCKER.lnk", bat, projeto, "ELEVA LOCKER - servidor")
If Err.Number <> 0 Then
    MsgBox "Erro atalho Desktop: " & Err.Description, vbCritical, "ELEVA LOCKER"
    WScript.Quit 1
End If

startup = shell.SpecialFolders("Startup")
Call CriarAtalho(startup & "\ELEVA LOCKER - Iniciar.lnk", bat, projeto, "ELEVA LOCKER - inicio Windows")
If Err.Number <> 0 Then
    MsgBox "Erro atalho Startup: " & Err.Description, vbCritical, "ELEVA LOCKER"
    WScript.Quit 1
End If

On Error GoTo 0

MsgBox "Atalhos criados!" & vbCrLf & vbCrLf & _
       "Desktop: ELEVA LOCKER.lnk" & vbCrLf & _
       "Iniciar: ELEVA LOCKER - Iniciar.lnk" & vbCrLf & vbCrLf & _
       "Destino: " & bat & vbCrLf & vbCrLf & _
       "Teste: duplo clique no atalho da Area de Trabalho.", _
       vbInformation, "ELEVA LOCKER"

WScript.Quit 0

Sub CriarAtalho(caminho, alvoBat, workdir, descricao)
    Dim s
    Set s = shell.CreateShortcut(caminho)
    s.TargetPath = alvoBat
    s.WorkingDirectory = workdir
    s.WindowStyle = 1
    s.Description = descricao
    s.IconLocation = "%SystemRoot%\System32\imageres.dll,109"
    s.Save
End Sub
