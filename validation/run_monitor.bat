@echo off
REM Data Validation Monitor - Run daily via Task Scheduler
REM
REM To schedule:
REM   1. Open Task Scheduler (taskschd.msc)
REM   2. Create Basic Task > Name: "Thesis Dashboard Validation"
REM   3. Trigger: Daily at 9:00 AM (or your preference)
REM   4. Action: Start a program
REM   5. Program: C:\Users\edwin\thesis_dashboard\validation\run_monitor.bat
REM   6. Start in: C:\Users\edwin\thesis_dashboard
REM

cd /d C:\Users\edwin\thesis_dashboard
python -m validation.monitor --validate --report

REM Keep window open if run manually (remove for silent scheduled runs)
if "%1"=="" pause
