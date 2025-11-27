#!/bin/bash
# Generate Allure test report

echo "Running BDD tests with Allure reporting..."

# Run tests with Allure formatter
behave -f allure_behave.formatter:AllureFormatter -o allure-results

# Check if allure command is available
if ! command -v allure &> /dev/null
then
    echo "Allure command not found. Installing..."
    echo "Please install Allure manually:"
    echo "  - macOS: brew install allure"
    echo "  - Linux: Download from https://github.com/allure-framework/allure2/releases"
    echo "  - Windows: scoop install allure"
    exit 1
fi

# Generate and serve report
echo "Generating Allure report..."
allure serve allure-results
