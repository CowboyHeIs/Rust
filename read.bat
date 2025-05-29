@echo off
setlocal enabledelayedexpansion

:: Normalize path and get absolute path
set "file=%~1"
set "file=!file:/=\!"

for %%A in ("%file%") do set "absfile=%%~fA"

:: Get current dir absolute path
set "curdir=%cd%"
set "curdir=!curdir:/=\!"

:: Compute relative path if possible
set "relfile=!absfile:%curdir%\=!"

:: If not relative (outside cwd), fallback to filename only
if "!relfile!"=="!absfile!" (
  for %%A in ("!absfile!") do set "relfile=%%~nxA"
)

:: Direct match fallback: if absfile not exists, try find by name
if not exist "!absfile!" (
  echo File not found directly. Searching...
  for /r %%F in ("*") do (
    if /i "%%~nxF"=="%~nx1" (
      set "absfile=%%F"
      :: recalc relfile
      set "absfile=!absfile:/=\!"
      set "relfile=!absfile:%curdir%\=!"
      if "!relfile!"=="!absfile!" (
        for %%A in ("!absfile!") do set "relfile=%%~nxA"
      )
      goto :found
    )
  )
  echo %~1 : Not Found
  exit /b 0
)

:found

:: Debugging statements to check paths
echo Processing file: !absfile!
echo Relative path: %relfile%

set "tmp=config/files_tmp.txt"
set "main=config/files.txt"
set copy=1
break > "%tmp%"

for /f "usebackq delims=" %%L in (`type "%main%" 2^>nul`) do (
  set "line=%%L"
  echo !line! | findstr /i /c:"%relfile% : ```" 2>nul
  if not errorlevel 1 (
    set copy=0
  ) else (
    echo !line! | findstr "^```$" 2>nul
    if not errorlevel 1 set copy=1
    if !copy! equ 1 >> "%tmp%" echo(!line!
  )
)
move /y "%tmp%" "%main%" >nul

:: Language detect
set "ext=%~x1"
set "lang="
if /i "%ext%"==".py" set "lang=python"
if /i "%ext%"==".js" set "lang=javascript"
if /i "%ext%"==".html" set "lang=html"
if /i "%ext%"==".css" set "lang=css"
if /i "%ext%"==".json" set "lang=json"
if /i "%ext%"==".java" set "lang=java"
if /i "%ext%"==".c" set "lang=c"
if /i "%ext%"==".cpp" set "lang=cpp"
if /i "%ext%"==".h" set "lang=c"
if /i "%ext%"==".sh" set "lang=bash"
if /i "%ext%"==".rb" set "lang=ruby"
if /i "%ext%"==".php" set "lang=php"
if /i "%ext%"==".xml" set "lang=xml"
if /i "%ext%"==".md" set "lang=markdown"
if /i "%ext%"==".sql" set "lang=sql"
if /i "%ext%"==".go" set "lang=go"
if /i "%ext%"==".ts" set "lang=typescript"
if /i "%ext%"==".bat" set "lang=batch"

:: Append new block with relfile header
if defined lang (
  >> "%main%" echo %relfile% : ```%lang%
) else (
  >> "%main%" echo %relfile% : ```
)

type "!absfile!" >> "%main%"
>> "%main%" echo ```

echo !absfile! : Added

exit /b 0
