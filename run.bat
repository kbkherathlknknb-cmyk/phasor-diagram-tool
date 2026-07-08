@echo off
echo Starting Phasor Diagram Tool...
python phasor_diagram.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error running phasor_diagram.py. Checking dependencies...
    pip install -r requirements.txt
    python phasor_diagram.py
)
pause
