@echo off
echo Starting Nile Key Frontend Server...
echo.

cd /d "%~dp0..\\frontend"

echo Checking for node_modules...
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

echo Starting frontend dev server on http://localhost:3000
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause