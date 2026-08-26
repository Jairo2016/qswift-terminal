@echo off
REM ============================================================
REM  INICIAR Q-SWIFT PUBLICO - AutoClaw 2026-08-26
REM  Arranca el servidor local + tunel publico cloudflared
REM ============================================================
cd /d "C:\Users\Jairo Omar\AGI_Workspace"
start "QSWIFT-SERVIDOR" cmd /k "python qswift_servidor_local.py"
timeout /t 3 /nobreak >nul
start "QSWIFT-TUNEL" cmd /k ""C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:8051 --no-autoupdate"
echo.
echo  Q-SWIFT LOCAL:  http://127.0.0.1:8051
echo  Q-SWIFT LAN:    http://192.168.100.47:8051
echo  TUNEL PUBLICO:  (lee la URL https://...trycloudflare.com de la ventana QSWIFT-TUNEL)
echo.
pause
