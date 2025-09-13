---
description: "Perform security audits using Gemini's analysis capabilities"
argument-hint: "[audit-type] [paths] - Types: sql_injection, xss, auth, general, input_validation"
allowed-tools: gemini_security_audit, Glob, Read
---

Perform comprehensive security audits on your codebase using Gemini's large context analysis.

Available audit types:
- `sql_injection` - Database query vulnerability analysis
- `xss` - Cross-site scripting vulnerability detection
- `auth` - Authentication and authorization security review
- `input_validation` - Input sanitization and validation analysis
- `general` - Comprehensive security assessment

Usage examples:
- `/gemini-audit sql_injection src/api src/database` - Check for SQL injection vulnerabilities
- `/gemini-audit auth src/middleware src/auth` - Review authentication security
- `/gemini-audit general .` - Comprehensive security audit of entire project

Arguments: $ARGUMENTS

I'll parse the audit type and paths from your arguments and perform the appropriate security analysis.