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