---
description: "Analyze specific files or directories using Gemini's large context window"
argument-hint: "[files/directories] [optional: analysis prompt]"
allowed-tools: gemini_analyze_files, gemini_analyze_directories, Read, Glob
---

Analyze the specified files or directories using Gemini's massive context window for comprehensive codebase analysis.

Usage examples:
- `/gemini-analyze src/main.py src/utils.py` - Analyze specific files
- `/gemini-analyze src/ tests/` - Analyze directories
- `/gemini-analyze @src/auth.py "explain the authentication flow"` - Analyze with custom prompt

I'll determine whether you've provided files or directories and use the appropriate Gemini analysis tool with the provided prompt or a comprehensive default analysis.

Files/directories to analyze: $ARGUMENTS