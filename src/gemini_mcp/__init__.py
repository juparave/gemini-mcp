#!/usr/bin/env python3
"""
Gemini MCP Server

An MCP server that provides tools for analyzing codebases using the Gemini CLI.
This server enables large-scale codebase analysis and verification using Gemini's
massive context window.
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Any, List, Optional
import asyncio
import json

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio


server = Server("gemini-mcp")

# Define available prompts
PROMPTS = {
    "analyze_files": {
        "name": "analyze_files",
        "description": "Analyze specific files using Gemini's large context window",
        "arguments": [
            {
                "name": "files",
                "description": "Comma-separated list of file paths to analyze",
                "required": True
            },
            {
                "name": "prompt",
                "description": "Custom analysis prompt (optional, defaults to comprehensive analysis)",
                "required": False
            }
        ]
    },
    "security_audit": {
        "name": "security_audit",
        "description": "Perform security audit on specified paths",
        "arguments": [
            {
                "name": "audit_type",
                "description": "Type of audit: sql_injection, xss, auth, general, input_validation",
                "required": True
            },
            {
                "name": "paths",
                "description": "Comma-separated list of paths to audit",
                "required": True
            }
        ]
    },
    "architecture_analysis": {
        "name": "architecture_analysis",
        "description": "Analyze codebase architecture and patterns",
        "arguments": [
            {
                "name": "analysis_type",
                "description": "Type of analysis: overview, dependencies, patterns, structure, coupling",
                "required": True
            },
            {
                "name": "paths",
                "description": "Comma-separated list of paths to analyze",
                "required": True
            }
        ]
    },
    "verify_feature": {
        "name": "verify_feature",
        "description": "Verify if a specific feature is implemented in the codebase",
        "arguments": [
            {
                "name": "feature_name",
                "description": "Name of the feature to verify (e.g., 'JWT authentication', 'rate limiting')",
                "required": True
            },
            {
                "name": "search_paths",
                "description": "Comma-separated list of paths to search (optional, defaults to current directory)",
                "required": False
            }
        ]
    },
    "project_overview": {
        "name": "project_overview",
        "description": "Get comprehensive overview of the entire project",
        "arguments": [
            {
                "name": "focus",
                "description": "Optional focus area (e.g., 'API architecture', 'data flow', 'security')",
                "required": False
            }
        ]
    }
}


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for Gemini CLI integration."""
    return [
        types.Tool(
            name="gemini_analyze_files",
            description="Analyze specific files using Gemini CLI with @ syntax",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of file paths to analyze (relative to current working directory)"
                    },
                    "prompt": {
                        "type": "string", 
                        "description": "Analysis prompt to send to Gemini"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory to run gemini command from (optional, defaults to current directory)"
                    }
                },
                "required": ["files", "prompt"]
            }
        ),
        types.Tool(
            name="gemini_analyze_directories",
            description="Analyze entire directories using Gemini CLI with @ syntax",
            inputSchema={
                "type": "object",
                "properties": {
                    "directories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of directory paths to analyze"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Analysis prompt to send to Gemini"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory to run gemini command from (optional)"
                    }
                },
                "required": ["directories", "prompt"]
            }
        ),
        types.Tool(
            name="gemini_analyze_all_files",
            description="Analyze all files in current directory using Gemini CLI --all_files flag",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Analysis prompt to send to Gemini"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory to run gemini command from (optional)"
                    }
                },
                "required": ["prompt"]
            }
        ),
        types.Tool(
            name="gemini_verify_implementation",
            description="Verify if specific features/patterns are implemented in the codebase",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {
                        "type": "string",
                        "description": "Name of the feature to verify (e.g., 'dark mode', 'JWT authentication')"
                    },
                    "search_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of directories/files to search in"
                    },
                    "verification_prompt": {
                        "type": "string",
                        "description": "Custom verification prompt (optional)"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory to run gemini command from (optional)"
                    }
                },
                "required": ["feature_name", "search_paths"]
            }
        ),
        types.Tool(
            name="gemini_security_audit",
            description="Perform security analysis of the codebase using Gemini",
            inputSchema={
                "type": "object",
                "properties": {
                    "audit_type": {
                        "type": "string",
                        "enum": ["sql_injection", "xss", "auth", "general", "input_validation"],
                        "description": "Type of security audit to perform"
                    },
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to audit (files or directories)"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory to run gemini command from (optional)"
                    }
                },
                "required": ["audit_type", "paths"]
            }
        ),
        types.Tool(
            name="gemini_architecture_analysis",
            description="Analyze codebase architecture and patterns using Gemini",
            inputSchema={
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["overview", "dependencies", "patterns", "structure", "coupling"],
                        "description": "Type of architectural analysis"
                    },
                    "paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Paths to analyze"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory to run gemini command from (optional)"
                    }
                },
                "required": ["analysis_type", "paths"]
            }
        )
    ]


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available prompts for Gemini analysis."""
    return [
        types.Prompt(
            name=prompt_info["name"],
            description=prompt_info["description"],
            arguments=[
                types.PromptArgument(
                    name=arg["name"],
                    description=arg["description"],
                    required=arg["required"]
                ) for arg in prompt_info["arguments"]
            ]
        ) for prompt_info in PROMPTS.values()
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict[str, str]) -> types.GetPromptResult:
    """Get a specific prompt with filled arguments."""
    if name not in PROMPTS:
        raise ValueError(f"Unknown prompt: {name}")

    if name == "analyze_files":
        files = arguments["files"].split(",") if "files" in arguments else []
        custom_prompt = arguments.get("prompt", "")

        if not files:
            raise ValueError("Files argument is required")

        if custom_prompt:
            prompt_text = f"Analyze these files: {', '.join(files)}\n\nSpecific analysis request: {custom_prompt}"
        else:
            prompt_text = f"Provide a comprehensive analysis of these files: {', '.join(files)}\n\nPlease explain:\n- Purpose and functionality of each file\n- Key components and their relationships\n- Code quality and patterns used\n- Any potential improvements or issues"

        return types.GetPromptResult(
            description=f"Analyze files: {', '.join(files)}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Use the gemini_analyze_files tool with files: {json.dumps(files)} and prompt: {json.dumps(prompt_text)}"
                    )
                )
            ]
        )

    elif name == "security_audit":
        audit_type = arguments.get("audit_type", "general")
        paths = arguments["paths"].split(",") if "paths" in arguments else ["."]

        return types.GetPromptResult(
            description=f"Security audit ({audit_type}) for: {', '.join(paths)}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Use the gemini_security_audit tool with audit_type: {json.dumps(audit_type)} and paths: {json.dumps(paths)}"
                    )
                )
            ]
        )

    elif name == "architecture_analysis":
        analysis_type = arguments.get("analysis_type", "overview")
        paths = arguments["paths"].split(",") if "paths" in arguments else ["."]

        return types.GetPromptResult(
            description=f"Architecture analysis ({analysis_type}) for: {', '.join(paths)}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Use the gemini_architecture_analysis tool with analysis_type: {json.dumps(analysis_type)} and paths: {json.dumps(paths)}"
                    )
                )
            ]
        )

    elif name == "verify_feature":
        feature_name = arguments.get("feature_name", "")
        search_paths = arguments.get("search_paths", ".").split(",") if arguments.get("search_paths") else ["."]

        if not feature_name:
            raise ValueError("Feature name is required")

        return types.GetPromptResult(
            description=f"Verify feature: {feature_name}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Use the gemini_verify_implementation tool with feature_name: {json.dumps(feature_name)} and search_paths: {json.dumps(search_paths)}"
                    )
                )
            ]
        )

    elif name == "project_overview":
        focus = arguments.get("focus", "")

        if focus:
            prompt_text = f"Provide a comprehensive overview of this entire project with a focus on: {focus}"
        else:
            prompt_text = "Provide a comprehensive overview of this entire project including architecture, main components, technologies used, and overall purpose."

        return types.GetPromptResult(
            description=f"Project overview{' (focus: ' + focus + ')' if focus else ''}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Use the gemini_analyze_all_files tool with prompt: {json.dumps(prompt_text)}"
                    )
                )
            ]
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")


async def run_gemini_command(
    args: List[str], 
    working_directory: Optional[str] = None
) -> tuple[str, str, int]:
    """Run a gemini command and return stdout, stderr, and return code."""
    try:
        cwd = working_directory if working_directory else os.getcwd()
        
        # Ensure gemini CLI is available
        process = await asyncio.create_subprocess_exec(
            "which", "gemini",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return "", "Gemini CLI not found. Please install gemini CLI first.", 1
        
        # Run the actual gemini command
        process = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode(), process.returncode
        
    except Exception as e:
        return "", f"Error running gemini command: {str(e)}", 1


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool calls for Gemini CLI integration."""
    
    if name == "gemini_analyze_files":
        files = arguments["files"]
        prompt = arguments["prompt"]
        working_directory = arguments.get("working_directory")
        
        # Build gemini command with @ syntax for files
        file_args = [f"@{file}" for file in files]
        full_prompt = " ".join(file_args) + " " + prompt
        
        cmd = ["gemini", "-p", full_prompt]
        stdout, stderr, returncode = await run_gemini_command(cmd, working_directory)
        
        if returncode != 0:
            return [types.TextContent(type="text", text=f"Error: {stderr}")]
        
        return [types.TextContent(type="text", text=stdout)]
    
    elif name == "gemini_analyze_directories":
        directories = arguments["directories"]
        prompt = arguments["prompt"]
        working_directory = arguments.get("working_directory")
        
        # Build gemini command with @ syntax for directories
        dir_args = [f"@{directory}/" for directory in directories]
        full_prompt = " ".join(dir_args) + " " + prompt
        
        cmd = ["gemini", "-p", full_prompt]
        stdout, stderr, returncode = await run_gemini_command(cmd, working_directory)
        
        if returncode != 0:
            return [types.TextContent(type="text", text=f"Error: {stderr}")]
        
        return [types.TextContent(type="text", text=stdout)]
    
    elif name == "gemini_analyze_all_files":
        prompt = arguments["prompt"]
        working_directory = arguments.get("working_directory")
        
        cmd = ["gemini", "--all_files", "-p", prompt]
        stdout, stderr, returncode = await run_gemini_command(cmd, working_directory)
        
        if returncode != 0:
            return [types.TextContent(type="text", text=f"Error: {stderr}")]
        
        return [types.TextContent(type="text", text=stdout)]
    
    elif name == "gemini_verify_implementation":
        feature_name = arguments["feature_name"]
        search_paths = arguments["search_paths"]
        verification_prompt = arguments.get("verification_prompt")
        working_directory = arguments.get("working_directory")
        
        # Build custom or default verification prompt
        if verification_prompt:
            prompt = verification_prompt
        else:
            prompt = f"Has {feature_name} been implemented in this codebase? Show me the relevant files and functions if it exists, or confirm if it's missing."
        
        # Build paths with @ syntax
        path_args = []
        for path in search_paths:
            if os.path.isdir(path):
                path_args.append(f"@{path}/")
            else:
                path_args.append(f"@{path}")
        
        full_prompt = " ".join(path_args) + " " + prompt
        
        cmd = ["gemini", "-p", full_prompt]
        stdout, stderr, returncode = await run_gemini_command(cmd, working_directory)
        
        if returncode != 0:
            return [types.TextContent(type="text", text=f"Error: {stderr}")]
        
        return [types.TextContent(type="text", text=stdout)]
    
    elif name == "gemini_security_audit":
        audit_type = arguments["audit_type"]
        paths = arguments["paths"]
        working_directory = arguments.get("working_directory")
        
        # Define security audit prompts
        audit_prompts = {
            "sql_injection": "Analyze this code for SQL injection vulnerabilities. Show how user inputs are sanitized and whether prepared statements or ORMs are used properly.",
            "xss": "Check for Cross-Site Scripting (XSS) vulnerabilities. Look for proper input sanitization and output encoding.",
            "auth": "Analyze the authentication and authorization implementation. Check for JWT handling, session management, and access controls.",
            "general": "Perform a general security audit. Look for common vulnerabilities like hardcoded secrets, insecure configurations, and improper error handling.",
            "input_validation": "Analyze input validation throughout the codebase. Check how user inputs are validated and sanitized."
        }
        
        prompt = audit_prompts.get(audit_type, audit_prompts["general"])
        
        # Build paths with @ syntax
        path_args = []
        for path in paths:
            if os.path.isdir(path):
                path_args.append(f"@{path}/")
            else:
                path_args.append(f"@{path}")
        
        full_prompt = " ".join(path_args) + " " + prompt
        
        cmd = ["gemini", "-p", full_prompt]
        stdout, stderr, returncode = await run_gemini_command(cmd, working_directory)
        
        if returncode != 0:
            return [types.TextContent(type="text", text=f"Error: {stderr}")]
        
        return [types.TextContent(type="text", text=stdout)]
    
    elif name == "gemini_architecture_analysis":
        analysis_type = arguments["analysis_type"]
        paths = arguments["paths"]
        working_directory = arguments.get("working_directory")
        
        # Define architecture analysis prompts
        analysis_prompts = {
            "overview": "Provide a high-level overview of this codebase architecture. Describe the main components, layers, and how they interact.",
            "dependencies": "Analyze the dependencies in this codebase. Show the dependency graph and identify any potential issues or circular dependencies.",
            "patterns": "Identify the architectural patterns and design patterns used in this codebase. Explain how they're implemented.",
            "structure": "Analyze the project structure and organization. Evaluate if it follows best practices and suggest improvements.",
            "coupling": "Analyze the coupling between different modules and components. Identify tightly coupled areas that could be refactored."
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["overview"])
        
        # Build paths with @ syntax
        path_args = []
        for path in paths:
            if os.path.isdir(path):
                path_args.append(f"@{path}/")
            else:
                path_args.append(f"@{path}")
        
        full_prompt = " ".join(path_args) + " " + prompt
        
        cmd = ["gemini", "-p", full_prompt]
        stdout, stderr, returncode = await run_gemini_command(cmd, working_directory)
        
        if returncode != 0:
            return [types.TextContent(type="text", text=f"Error: {stderr}")]
        
        return [types.TextContent(type="text", text=stdout)]
    
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Main entry point for the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gemini-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())