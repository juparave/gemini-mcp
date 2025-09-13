#!/usr/bin/env python3
"""
Main entry point for running the Gemini MCP server directly.
"""

from gemini_mcp import main


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
