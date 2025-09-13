---
description: "Verify if specific features or patterns are implemented in the codebase"
argument-hint: "[feature-name] [search-paths] - e.g., 'JWT authentication' src/"
allowed-tools: gemini_verify_implementation, Grep, Glob, Read
---

Verify whether specific features, patterns, or implementations exist in your codebase using Gemini's comprehensive analysis.

This command helps answer questions like:
- "Does this codebase have JWT authentication?"
- "Is rate limiting implemented?"
- "Are there any error handling patterns?"
- "Is there a caching mechanism?"

Usage examples:
- `/gemini-verify "JWT authentication" src/` - Check for JWT auth implementation
- `/gemini-verify "rate limiting" src/api src/middleware` - Look for rate limiting
- `/gemini-verify "error handling" .` - Verify error handling patterns across project
- `/gemini-verify "database migrations" src/database migrations/` - Check migration system

Arguments: $ARGUMENTS

I'll parse the feature name and search paths to thoroughly verify if the specified functionality is implemented in your codebase.