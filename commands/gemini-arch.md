---
description: "Analyze codebase architecture and patterns using Gemini"
argument-hint: "[analysis-type] [paths] - Types: overview, dependencies, patterns, structure, coupling"
allowed-tools: gemini_architecture_analysis, Glob, Read
---

Analyze your codebase architecture and design patterns using Gemini's comprehensive analysis capabilities.

Available analysis types:
- `overview` - High-level architectural understanding and summary
- `dependencies` - Dependency mapping and analysis
- `patterns` - Design pattern identification and usage
- `structure` - Code organization and structural analysis
- `coupling` - Component coupling and cohesion analysis

Usage examples:
- `/gemini-arch overview src` - Get architectural overview of source code
- `/gemini-arch dependencies .` - Analyze project dependencies
- `/gemini-arch patterns src/components` - Identify design patterns in components
- `/gemini-arch coupling src/api src/services` - Analyze coupling between API and services

Arguments: $ARGUMENTS

I'll parse the analysis type and paths to provide detailed architectural insights about your codebase.