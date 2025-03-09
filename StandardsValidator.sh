#!/bin/bash
# File: StandardsValidator.sh
# Path: OllamaModelEditor/StandardsValidator.sh
# Standard: AIDEV-PascalCase-1.0
# Standards validator for AIDEV-PascalCase compliance

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

echo -e "${BOLD}AIDEV-PascalCase Standards Validator${RESET}\n"

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON=python3
else
    PYTHON=python
fi

# Define function to print a separator line
PrintSeparator() {
    echo -e "\n${YELLOW}============================================================${RESET}\n"
}

# Check if we have the standards checker script
if [ ! -f "CheckStandards.py" ]; then
    echo -e "${RED}Error: standards checker script (CheckStandards.py) not found!${RESET}"
    exit 1
fi

# Step 1: Run the standards checker
PrintSeparator
echo -e "${BOLD}Running Standards Checker...${RESET}"
$PYTHON CheckStandards.py
STANDARDS_RESULT=$?

# Step 2: Validate specific high-risk files manually
PrintSeparator
echo -e "${BOLD}Validating Critical Files...${RESET}"

# List of critical files to check explicitly
CRITICAL_FILES=(
    "RunTest.py"
    "Main.py"
    "AI/__init__.py"
    "Core/__init__.py"
    "UI/__init__.py"
    "Utils/__init__.py"
)

# Patterns to check (focusing on function and variable naming)
CHECK_PATTERNS=(
    "def [a-z]"  # Functions that don't start with uppercase
    "self\.[a-z]" # Instance variables that don't start with uppercase
)

CRITICAL_ISSUES=0

for FILE in "${CRITICAL_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        echo -e "Checking ${YELLOW}$FILE${RESET}..."
        
        # Check each pattern
        for PATTERN in "${CHECK_PATTERNS[@]}"; do
            MATCHES=$($PYTHON -c "
import re
with open('$FILE', 'r') as f:
    content = f.read()
    matches = re.findall(r'$PATTERN', content)
    for match in matches:
        print(f'  - {match.strip()}')
" 2>/dev/null)
            
            if [ ! -z "$MATCHES" ]; then
                echo -e "${RED}Found non-compliant patterns:${RESET}"
                echo -e "$MATCHES"
                CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
            fi
        done
        
        # Check for special terms
        SPECIAL_TERMS=("ai" "db" "gui" "api")
        for TERM in "${SPECIAL_TERMS[@]}"; do
            if grep -i "\b$TERM\b" "$FILE" | grep -v -E "\".*\b$TERM\b.*\"" | grep -v -E "'.*\b$TERM\b.*'" | grep -v -i "\b${TERM^^}\b" &>/dev/null; then
                echo -e "${RED}Found special term '$TERM' not in proper capitalization (should be ${TERM^^})${RESET}"
                CRITICAL_ISSUES=$((CRITICAL_ISSUES + 1))
            fi
        done
        
        if [ $CRITICAL_ISSUES -eq 0 ]; then
            echo -e "${GREEN}No issues found in $FILE${RESET}"
        fi
    else
        echo -e "${YELLOW}Warning: Critical file $FILE not found${RESET}"
    fi
done

# Step 3: Verify header in new files
PrintSeparator
echo -e "${BOLD}Checking Headers in Recently Modified Files...${RESET}"

# Get list of Python files modified in the last day, excluding ..Exclude directory
RECENT_FILES=$(find . -name "*.py" -type f -mtime -1 -not -path "*..Exclude*" -not -path "*.venv*" -not -path "*__pycache__*" -not -path "*.git*" 2>/dev/null)

HEADER_ISSUES=0
for FILE in $RECENT_FILES; do
    if ! grep -q "# Standard: AIDEV-PascalCase-1.0" "$FILE"; then
        echo -e "${RED}Missing standard header in recently modified file: $FILE${RESET}"
        HEADER_ISSUES=$((HEADER_ISSUES + 1))
    fi
done

if [ $HEADER_ISSUES -eq 0 ]; then
    echo -e "${GREEN}All recently modified files have proper headers${RESET}"
else
    echo -e "${RED}Found $HEADER_ISSUES files with missing headers${RESET}"
fi

# Step 4: Final assessment
PrintSeparator
echo -e "${BOLD}Standards Validation Summary${RESET}"

if [ $STANDARDS_RESULT -eq 0 ] && [ $CRITICAL_ISSUES -eq 0 ] && [ $HEADER_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ All validation checks passed!${RESET}"
    echo -e "${GREEN}The codebase complies with AIDEV-PascalCase standards.${RESET}"
    EXIT_CODE=0
else
    echo -e "${RED}❌ Standards validation failed!${RESET}"
    echo -e "${YELLOW}Please address the following issues:${RESET}"
    
    if [ $STANDARDS_RESULT -ne 0 ]; then
        echo -e "  - General standards check failed"
    fi
    
    if [ $CRITICAL_ISSUES -ne 0 ]; then
        echo -e "  - $CRITICAL_ISSUES issues found in critical files"
    fi
    
    if [ $HEADER_ISSUES -ne 0 ]; then
        echo -e "  - $HEADER_ISSUES files missing proper headers"
    fi
    
    EXIT_CODE=1
fi

exit $EXIT_CODE