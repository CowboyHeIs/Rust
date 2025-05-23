@echo off
setlocal enabledelayedexpansion
set PROMPT=

:: Default keep list
set "ND_LIST=ai.py;ai.bat;log.txt;debug.txt;NoDelete.txt;files.txt"

if exist NoDelete.txt (
  for /f "usebackq delims=" %%L in ("NoDelete.txt") do (
    if "!ND_LIST!"=="" (
      set "ND_LIST=%%L"
    ) else (
      set "ND_LIST=!ND_LIST!;%%L"
    )
  )
)

:loop
if "%~1"=="" goto run
if defined PROMPT (
  set PROMPT=!PROMPT! %~1
) else (
  set PROMPT=%~1
)
shift
goto loop

:run
python ai.py "!PROMPT!" < log.txt > ai_response.txt

type ai_response.txt

del ai_response.txt

for %%F in (*.*) do (
  set "file=%%F"
  set "skip=no"
  for %%N in (!ND_LIST!) do (
    if /I "%%N"=="!file!" set "skip=yes"
  )
  if "!skip!"=="no" (
    del /F /Q "!file!"
  )
)
