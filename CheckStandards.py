# File: CheckStandards.py
# Path: OllamaModelEditor/CheckStandards.py
# Standard: AIDEV-PascalCase-1.0
# A utility to verify adherence to the AIDEV-PascalCase standards

import os
import re
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

class StandardsChecker:
    """Checks Python files for adherence to AIDEV-PascalCase standards."""
    
    def __init__(self, root_dir: str = "."):
        """Initialize the standards checker.
        
        Args:
            root_dir: Root directory to scan for Python files
        """
        self.RootDir = root_dir
        self.SetupLogger()
        self.LoadSpecialTerms()
        self.IgnorePatterns = self.LoadIgnorePatterns()
        
        # Statistics
        self.TotalFiles = 0
        self.FilesWithIssues = 0
        self.TotalIssues = 0
        self.IssueTypes = {}
    
    def SetupLogger(self):
        """Set up the logger."""
        self.Logger = logging.getLogger("StandardsChecker")
        self.Logger.setLevel(logging.INFO)
        
        Handler = logging.StreamHandler()
        Formatter = logging.Formatter('%(levelname)s: %(message)s')
        Handler.setFormatter(Formatter)
        self.Logger.addHandler(Handler)
    
    def LoadSpecialTerms(self):
        """Load special terms that should always be capitalized in a specific way."""
        self.SpecialTerms = {
            "ai": "AI",
            "db": "DB",
            "gui": "GUI",
            "api": "API"
        }
    
    def LoadIgnorePatterns(self) -> List[str]:
        """Load patterns to ignore from .gitignore and add custom ignores.
        
        Returns:
            List[str]: List of ignore patterns
        """
        Patterns = [
            "**/__pycache__/**",
            "**/.venv/**",
            "**/venv/**",
            "**/env/**",
            "**/.git/**"
        ]
        
        # Add explicit pattern for ..Exclude directory
        Patterns.append("..Exclude/**")
        
        # Try to load .gitignore patterns
        GitignorePath = os.path.join(self.RootDir, ".gitignore")
        if os.path.exists(GitignorePath):
            try:
                with open(GitignorePath, 'r', encoding='utf-8') as file:
                    for Line in file:
                        Line = Line.strip()
                        if Line and not Line.startswith('#'):
                            Patterns.append(Line)
                            
                self.Logger.info(f"Loaded {len(Patterns)} ignore patterns from .gitignore")
            except Exception as e:
                self.Logger.error(f"Error loading .gitignore: {e}")
        
        return Patterns
    
    def ShouldIgnore(self, file_path: str) -> bool:
        """Check if a file should be ignored based on ignore patterns.
        
        Args:
            file_path: Path to check
            
        Returns:
            bool: True if the file should be ignored
        """
        # Add debug output
        self.Logger.debug(f"Checking if file should be ignored: {file_path}")
        
        RelativePath = os.path.relpath(file_path, self.RootDir)
        
        # Add debug output
        self.Logger.debug(f"  Relative path: {RelativePath}")
        
        # Check for ..Exclude directory explicitly
        if "..Exclude" in RelativePath:
            self.Logger.debug(f"  Ignoring file in ..Exclude directory: {file_path}")
            return True
            
        for Pattern in self.IgnorePatterns:
            # Simple direct match
            if Pattern == RelativePath:
                self.Logger.debug(f"  Ignoring file: direct match with pattern '{Pattern}'")
                return True
            
            # Directory match (e.g., "dir/")
            if Pattern.endswith('/') and RelativePath.startswith(Pattern):
                self.Logger.debug(f"  Ignoring file: directory match with pattern '{Pattern}'")
                return True
            
            # File extension match (e.g., "*.py")
            if Pattern.startswith('*.') and RelativePath.endswith(Pattern[1:]):
                self.Logger.debug(f"  Ignoring file: extension match with pattern '{Pattern}'")
                return True
            
            # Wildcard directory match (e.g., "**/dir/**")
            if '**' in Pattern:
                # Replace ** with wildcard regex
                RegexPattern = Pattern.replace('**', '.*').replace('*', '[^/]*').replace('?', '.')
                if re.match(f"^{RegexPattern}$", RelativePath):
                    self.Logger.debug(f"  Ignoring file: wildcard directory match with pattern '{Pattern}'")
                    return True
            
            # Simple wildcard (e.g., "*.py")
            elif '*' in Pattern or '?' in Pattern:
                # Convert glob pattern to regex
                RegexPattern = Pattern.replace('.', '\\.').replace('*', '.*').replace('?', '.')
                if re.match(f"^{RegexPattern}$", RelativePath):
                    self.Logger.debug(f"  Ignoring file: wildcard match with pattern '{Pattern}'")
                    return True
        
        return False
    
    def FindPythonFiles(self) -> List[str]:
        """Find all Python files in the project.
        
        Returns:
            List[str]: List of Python file paths
        """
        PythonFiles = []
        AllFiles = []
        IgnoredFiles = []
        
        self.Logger.info(f"Searching for Python files in {self.RootDir}")
        
        for Root, Dirs, Files in os.walk(self.RootDir):
            # Skip directories that should be ignored
            DirsToRemove = []
            for Dir in Dirs:
                DirPath = os.path.join(Root, Dir)
                # Skip directories that start with . or ..
                if Dir.startswith('.') or Dir.startswith('..'):
                    DirsToRemove.append(Dir)
                    self.Logger.debug(f"Skipping directory: {DirPath}")
                    continue
                
                # Check if directory should be ignored
                if self.ShouldIgnore(DirPath):
                    DirsToRemove.append(Dir)
                    self.Logger.debug(f"Ignoring directory: {DirPath}")
            
            # Remove directories that should be ignored
            for Dir in DirsToRemove:
                Dirs.remove(Dir)
            
            for File in Files:
                if File.endswith(".py"):
                    FilePath = os.path.join(Root, File)
                    AllFiles.append(FilePath)
                    
                    if not self.ShouldIgnore(FilePath):
                        PythonFiles.append(FilePath)
                        self.Logger.debug(f"Found Python file: {FilePath}")
                    else:
                        IgnoredFiles.append(FilePath)
                        self.Logger.debug(f"Ignoring Python file: {FilePath}")
        
        self.Logger.info(f"Found {len(AllFiles)} total Python files")
        self.Logger.info(f"Ignoring {len(IgnoredFiles)} Python files")
        self.Logger.info(f"Checking {len(PythonFiles)} Python files")
        
        self.TotalFiles = len(PythonFiles)
        return PythonFiles
    
    def CheckFileHeader(self, file_path: str) -> bool:
        """Check if a file has the correct AIDEV-PascalCase header.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            bool: True if the header is valid, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                Content = file.read()
                
                # Check for standard header format
                HeaderPattern = r"# File: .*?\n# Path: .*?\n# Standard: AIDEV-PascalCase-1\.0"
                if not re.search(HeaderPattern, Content, re.DOTALL):
                    self.Logger.debug(f"Missing or incorrect header in {file_path}")
                    self.IncrementIssue("missing_header")
                    return False
                
                return True
        except Exception as e:
            self.Logger.error(f"Error checking header for {file_path}: {e}")
            return False
    
    def CheckFunctionNames(self, file_path: str) -> List[str]:
        """Check function names for PascalCase.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List[str]: List of non-compliant function names
        """
        Issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                Content = file.read()
                
                # Find all function definitions
                FuncPattern = r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\("
                Functions = re.findall(FuncPattern, Content)
                
                # Skip system-level functions
                SystemFuncs = {"__init__", "__str__", "__repr__", "__call__", "__enter__", "__exit__"}
                
                for Func in Functions:
                    if Func in SystemFuncs:
                        continue
                        
                    # Check for PascalCase (first letter capitals and capitals after underscore)
                    PascalPattern = r"^[A-Z][a-zA-Z0-9]*(_[A-Z][a-zA-Z0-9]*)*$"
                    if not re.match(PascalPattern, Func):
                        Issues.append(Func)
                        self.IncrementIssue("non_pascal_function")
                
                return Issues
        except Exception as e:
            self.Logger.error(f"Error checking function names for {file_path}: {e}")
            return []
    
    def CheckClassNames(self, file_path: str) -> List[str]:
        """Check class names for PascalCase.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List[str]: List of non-compliant class names
        """
        Issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                Content = file.read()
                
                # Find all class definitions
                ClassPattern = r"class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(\(|:)"
                Classes = re.findall(ClassPattern, Content)
                
                for ClassName, _ in Classes:
                    # Check for PascalCase
                    PascalPattern = r"^[A-Z][a-zA-Z0-9]*$"
                    if not re.match(PascalPattern, ClassName):
                        Issues.append(ClassName)
                        self.IncrementIssue("non_pascal_class")
                
                return Issues
        except Exception as e:
            self.Logger.error(f"Error checking class names for {file_path}: {e}")
            return []
    
    def CheckVariableNames(self, file_path: str) -> List[str]:
        """Check variable assignment for PascalCase.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List[str]: List of non-compliant variable names
        """
        Issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                Content = file.read()
                
                # Find variable assignments in classes and methods (member variables)
                VarPattern = r"self\.([a-zA-Z_][a-zA-Z0-9_]*)\s*="
                Variables = re.findall(VarPattern, Content)
                
                # Also check regular variable assignments (harder to be accurate)
                # This might catch some function calls, so we'll be conservative
                VarPattern2 = r"^[^#]*?([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?![=])"
                for Line in Content.split('\n'):
                    if "def " not in Line and "class " not in Line and "import " not in Line:
                        Match = re.match(VarPattern2, Line.strip())
                        if Match:
                            Variables.append(Match.group(1))
                
                # Remove duplicates and filter out system variables and keywords
                Variables = set(Variables)
                SystemVars = {"self", "cls", "args", "kwargs", "None", "True", "False"}
                PythonKeywords = {
                    "and", "as", "assert", "break", "class", "continue", "def", "del", "elif",
                    "else", "except", "finally", "for", "from", "global", "if", "import", "in",
                    "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
                    "while", "with", "yield"
                }
                
                for Var in Variables:
                    if Var in SystemVars or Var in PythonKeywords or Var.startswith("__"):
                        continue
                    
                    # Check for PascalCase
                    PascalPattern = r"^[A-Z][a-zA-Z0-9]*(_[A-Z][a-zA-Z0-9]*)*$"
                    if not re.match(PascalPattern, Var):
                        Issues.append(Var)
                        self.IncrementIssue("non_pascal_variable")
                
                return Issues
        except Exception as e:
            self.Logger.error(f"Error checking variable names for {file_path}: {e}")
            return []
    
    def CheckSpecialTerms(self, file_path: str) -> List[Tuple[str, str]]:
        """Check special terms for correct capitalization.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List[Tuple[str, str]]: List of (incorrect term, correct form) pairs
        """
        Issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                Content = file.read()
                
                for TermLower, TermCorrect in self.SpecialTerms.items():
                    # We'll look for the term as a word boundary
                    # but exclude cases where it's part of a string literal
                    Pattern = r'\b(' + TermLower + r'|' + TermLower.capitalize() + r')\b'
                    
                    # Find all instances outside of string literals (simplified approach)
                    Lines = Content.split('\n')
                    for i, Line in enumerate(Lines):
                        # Skip comments and strings
                        if Line.strip().startswith('#') or Line.strip().startswith('"') or Line.strip().startswith("'"):
                            continue
                            
                        Matches = re.findall(Pattern, Line, re.IGNORECASE)
                        for Match in Matches:
                            if Match != TermCorrect:
                                Issues.append((Match, TermCorrect))
                                self.IncrementIssue("special_term")
                
                return Issues
        except Exception as e:
            self.Logger.error(f"Error checking special terms for {file_path}: {e}")
            return []
    
    def IncrementIssue(self, issue_type: str):
        """Increment the count for an issue type.
        
        Args:
            issue_type: Type of issue
        """
        self.TotalIssues += 1
        self.IssueTypes[issue_type] = self.IssueTypes.get(issue_type, 0) + 1
    
    def CheckFile(self, file_path: str) -> bool:
        """Check a file for adherence to standards.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            bool: True if the file passes all checks, False otherwise
        """
        self.Logger.debug(f"Checking {file_path}...")
        HasIssues = False
        
        # Check header
        if not self.CheckFileHeader(file_path):
            HasIssues = True
        
        # Check function names
        FunctionIssues = self.CheckFunctionNames(file_path)
        if FunctionIssues:
            HasIssues = True
            self.Logger.debug(f"Function names not in PascalCase: {', '.join(FunctionIssues)}")
        
        # Check class names
        ClassIssues = self.CheckClassNames(file_path)
        if ClassIssues:
            HasIssues = True
            self.Logger.debug(f"Class names not in PascalCase: {', '.join(ClassIssues)}")
        
        # Check variable names
        VarIssues = self.CheckVariableNames(file_path)
        if VarIssues:
            HasIssues = True
            self.Logger.debug(f"Variable names not in PascalCase: {', '.join(VarIssues)}")
        
        # Check special terms
        TermIssues = self.CheckSpecialTerms(file_path)
        if TermIssues:
            HasIssues = True
            for Incorrect, Correct in TermIssues:
                self.Logger.debug(f"Special term should be {Correct}, found {Incorrect}")
        
        if HasIssues:
            self.FilesWithIssues += 1
            
        return not HasIssues
    
    def RunChecks(self) -> bool:
        """Run standards checks on all Python files.
        
        Returns:
            bool: True if all files pass, False otherwise
        """
        self.Logger.info("Starting AIDEV-PascalCase Standards check...")
        
        # First, just list some files to debug
        self.Logger.info(f"Checking current directory contents:")
        try:
            files = os.listdir(self.RootDir)
            for file in files:
                self.Logger.info(f"  - {file}")
        except Exception as e:
            self.Logger.error(f"Error listing directory contents: {e}")
        
        PythonFiles = self.FindPythonFiles()
        self.Logger.info(f"Found {len(PythonFiles)} Python files to check.")
        
        # If no files found, print more details
        if not PythonFiles:
            self.Logger.info("No Python files found! Checking .gitignore patterns:")
            for Pattern in self.IgnorePatterns:
                self.Logger.info(f"  - {Pattern}")
            
            # Check a few known files explicitly
            KnownFiles = ["Main.py", "RunTest.py", "CheckStandards.py"]
            for FileName in KnownFiles:
                FilePath = os.path.join(self.RootDir, FileName)
                if os.path.exists(FilePath):
                    self.Logger.info(f"Found {FileName} but it's being ignored")
                    # Check why it's being ignored
                    if self.ShouldIgnore(FilePath):
                        self.Logger.info(f"  {FileName} is being ignored by a pattern")
                else:
                    self.Logger.info(f"{FileName} doesn't exist in the root directory")
        
        AllPass = True
        for FilePath in PythonFiles:
            FilePass = self.CheckFile(FilePath)
            AllPass = AllPass and FilePass
        
        # Print summary
        self.Logger.info("\n=== Standards Check Summary ===")
        self.Logger.info(f"Total files checked: {self.TotalFiles}")
        self.Logger.info(f"Files with issues: {self.FilesWithIssues}")
        self.Logger.info(f"Total issues found: {self.TotalIssues}")
        
        if self.IssueTypes:
            self.Logger.info("Issues by type:")
            for IssueType, Count in self.IssueTypes.items():
                self.Logger.info(f"  - {IssueType}: {Count}")
        
        if AllPass:
            self.Logger.info("✅ All files pass the AIDEV-PascalCase standards check!")
        else:
            self.Logger.warning("❌ Some files do not meet the AIDEV-PascalCase standards.")
        
        return AllPass

def Main():
    """Main function."""
    # Get the root directory from command line arguments or use current directory
    RootDir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Setup logging to be more verbose
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    Checker = StandardsChecker(RootDir)
    Passed = Checker.RunChecks()
    
    # Exit with appropriate status code
    sys.exit(0 if Passed else 1)

if __name__ == "__main__":
    Main()
