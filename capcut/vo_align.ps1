# Where each sentence and word of a known voice-over script is spoken, with Windows' own speech recogniser (built
# into Windows, nothing to install).
#   powershell -ExecutionPolicy Bypass -File capcut/vo_align.ps1 <voice.wav> <script.txt>
# script.txt holds the voice-over, one sentence a line. Prints one line per sentence heard, in the order spoken:
#   <sentence index from 0> <start s> <end s> <start of each word, comma separated>
# The recogniser only listens for the script's own sentences (a grammar), so it does not have to guess the words, only
# when they are said. build_project.py uses it on Windows to put each on-screen line up when the voice says the words
# that line carries (text that appears before its words are spoken reads as a mistake).
param([string]$wav, [string]$script)
Add-Type -AssemblyName System.Speech
$culture = New-Object System.Globalization.CultureInfo("en-US")
$eng = New-Object System.Speech.Recognition.SpeechRecognitionEngine($culture)
$lines = @(Get-Content -LiteralPath $script -Encoding UTF8 | Where-Object { $_.Trim() -ne "" })
$choices = New-Object System.Speech.Recognition.Choices
for ($i = 0; $i -lt $lines.Count; $i++) {
  $words = ($lines[$i].ToLower() -replace "-", " " -replace "[^a-z0-9' ]", " ").Split(" ", [StringSplitOptions]::RemoveEmptyEntries)
  $gb = New-Object System.Speech.Recognition.GrammarBuilder
  $gb.Culture = $culture
  $gb.Append([string]::Join(" ", $words))
  $choices.Add((New-Object System.Speech.Recognition.SemanticResultValue($gb, [string]$i)).ToGrammarBuilder())
}
$top = New-Object System.Speech.Recognition.GrammarBuilder($choices)
$top.Culture = $culture
$eng.LoadGrammar((New-Object System.Speech.Recognition.Grammar($top)))
$eng.SetInputToWaveFile($wav)
$eng.BabbleTimeout = [TimeSpan]::FromSeconds(0)
$eng.EndSilenceTimeout = [TimeSpan]::FromSeconds(0.1)
$eng.EndSilenceTimeoutAmbiguous = [TimeSpan]::FromSeconds(0.2)
$global:out = New-Object System.Collections.ArrayList
$global:done = $false
Register-ObjectEvent -InputObject $eng -EventName SpeechRecognized -Action {
  $r = $EventArgs.Result; $a = $r.Audio; $ws = @()
  foreach ($w in $r.Words) { try { $ws += "{0:N2}" -f $r.GetAudioForWordRange($w, $w).AudioPosition.TotalSeconds } catch { $ws += "-" } }
  [void]$global:out.Add(("{0} {1:N2} {2:N2} {3}" -f $r.Semantics.Value, $a.AudioPosition.TotalSeconds, ($a.AudioPosition + $a.Duration).TotalSeconds, [string]::Join(",", $ws)))
} | Out-Null
Register-ObjectEvent -InputObject $eng -EventName RecognizeCompleted -Action { $global:done = $true } | Out-Null
$eng.RecognizeAsync([System.Speech.Recognition.RecognizeMode]::Multiple)
$t = 0
while (-not $global:done -and $t -lt 600) { Start-Sleep -Milliseconds 100; $t++ }
$global:out
