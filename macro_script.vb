Option Explicit
Dim i As Integer

Sub RunPythonScript()
    Dim objShell As Object
    Dim pythonExe As String, scriptPath As String, cmd As String
    Dim inputCell As Range, outputCell As Range
    Dim outputData As Variant, data As Variant

    ' Set the paths to your Python executable and the script
    pythonExe = "C:\Users\ethan\AppData\Local\Programs\Python\Python311\python.exe"
    scriptPath = "C:\Users\ethan\Desktop\CarScript\main.py"

    ' Get the currently selected cell in Excel
    Set inputCell = Selection
    Set outputCell = inputCell.Offset(0, 1)

    ' Prepare the command to run the Python script
    cmd = pythonExe & " " & scriptPath & " " & inputCell.Value

    ' Run the Python script and capture the output
    Set objShell = CreateObject("WScript.Shell")
    outputData = objShell.Exec(cmd).StdOut.ReadAll

    ' Split the output data and write it to Excel cells
    data = Split(outputData, ",")
    For i = LBound(data) To UBound(data)
        If IsNumeric(data(i)) Then
            outputCell.Offset(0, i).Value = CDbl(data(i))
        Else
            outputCell.Offset(0, i).Value = data(i)
        End If
    Next i

End Sub
