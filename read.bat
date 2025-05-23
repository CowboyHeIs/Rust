@echo off
setlocal enabledelayedexpansion

:: Replace / with \ in filepath
set "file=%~1"
set "file=!file:/=\!"

:: Direct match
if not exist "!file!" (
  :: Search subfolders if not found
  for /r %%F in ("*") do (
    if /i "%%~nxF"=="%~nx1" (
      set "file=%%F"
      goto :found
    )
  )
  echo %~1 : Not Found
  exit /b 0
)

:found
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

if defined lang (
  >> files.txt echo !file! : ```!lang!
) else (
  >> files.txt echo !file! : ```
)

type "!file!" >> files.txt
>> files.txt echo ```
echo !file! : Added
exit /b 0
