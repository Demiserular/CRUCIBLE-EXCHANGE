@echo off
REM Generate Allure test report (Windows version)

echo Running BDD tests with Allure reporting...

REM Run tests with Allure formatter
behave -f allure_behave.formatter:AllureFormatter -o allure-results

REM Check if allure command is available
where allure >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Allure command not found. Installing...
    echo Please install Allure manually:
    echo   - Windows: scoop install allure
    echo   - Or download from https://github.com/allure-framework/allure2/releases
    exit /b 1
)

REM Generate and serve report
echo Generating Allure report...
allure serve allure-results
