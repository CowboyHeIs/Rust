@echo off
setlocal enabledelayedexpansion
set PROMPT=

:: Keep only essential and config files
set "ND_LIST=ai.py;ai.bat;read.bat;README.md"

if exist config/NoDelete.txt (
  for /f "usebackq delims=" %%L in ("config/NoDelete.txt") do (
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
python ai.py "!PROMPT!" < config/log.txt > ai_response.txt

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
