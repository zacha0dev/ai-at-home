@echo off
title Enable OpenSSH  -  RUN AS ADMINISTRATOR
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0enable-ssh.ps1"
