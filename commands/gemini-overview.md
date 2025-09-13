---
description: "Get a comprehensive overview of the entire project using Gemini's large context window"
argument-hint: "[optional: custom prompt]"
allowed-tools: gemini_analyze_all_files, Read, Glob
---

Get a comprehensive overview of your entire project using Gemini's massive context window to analyze all files at once.

This command is perfect for:
- Understanding new codebases
- Generating project documentation
- Getting architectural overviews
- Onboarding team members
- Creating project summaries

Usage examples:
- `/gemini-overview` - Standard comprehensive project overview
- `/gemini-overview "focus on the API architecture"` - Custom analysis focus
- `/gemini-overview "explain this for a new developer"` - Onboarding-focused overview
- `/gemini-overview "identify potential refactoring opportunities"` - Improvement focus

Custom prompt (optional): $ARGUMENTS

I'll analyze all files in the current directory to provide a thorough understanding of your project's structure, purpose, and implementation.