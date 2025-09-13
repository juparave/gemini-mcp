#!/bin/bash

# Gemini MCP Claude Configuration Installer
# This script installs Claude commands and agents for the Gemini MCP server

set -e

# Get the directory where this script is actually located (resolving symlinks)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
    SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$SCRIPT_DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if files exist
check_source_files() {
    local missing_files=()

    if [ ! -d "$SCRIPT_DIR/commands" ]; then
        missing_files+=("commands directory")
    fi

    if [ ! -f "$SCRIPT_DIR/agent__gemini-analyzer.md" ]; then
        missing_files+=("agent__gemini-analyzer.md")
    fi

    # Check for command files
    local commands=("gemini-analyze" "gemini-audit" "gemini-arch" "gemini-verify" "gemini-overview")
    for cmd in "${commands[@]}"; do
        if [ ! -f "$SCRIPT_DIR/commands/${cmd}.md" ]; then
            missing_files+=("commands/${cmd}.md")
        fi
    done

    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "Missing required files in $SCRIPT_DIR:"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi
}

# Function to install locally (project-specific)
install_local() {
    print_info "Installing Claude configuration locally (project-specific)..."
    print_info "Current directory: $(pwd)"

    local target_dir=".claude"

    # Create directories
    mkdir -p "$target_dir/commands"
    mkdir -p "$target_dir/agents"

    # Copy command files
    print_info "Copying command files from $SCRIPT_DIR/commands/..."
    cp "$SCRIPT_DIR/commands"/*.md "$target_dir/commands/"
    print_success "Commands installed to $target_dir/commands/"

    # Copy agent file
    print_info "Copying agent files from $SCRIPT_DIR/..."
    cp "$SCRIPT_DIR/agent__gemini-analyzer.md" "$target_dir/agents/gemini-analyzer.md"
    print_success "Agent installed to $target_dir/agents/"

    print_success "Local installation complete!"
    print_info "Commands and agent are now available for this project only."
}

# Function to install globally (user-wide)
install_global() {
    print_info "Installing Claude configuration globally (user-wide)..."

    local target_dir="$HOME/.claude"

    # Create directories
    mkdir -p "$target_dir/commands"
    mkdir -p "$target_dir/agents"

    # Copy command files
    print_info "Copying command files from $SCRIPT_DIR/commands/..."
    cp "$SCRIPT_DIR/commands"/*.md "$target_dir/commands/"
    print_success "Commands installed to $target_dir/commands/"

    # Copy agent file
    print_info "Copying agent files from $SCRIPT_DIR/..."
    cp "$SCRIPT_DIR/agent__gemini-analyzer.md" "$target_dir/agents/gemini-analyzer.md"
    print_success "Agent installed to $target_dir/agents/"

    print_success "Global installation complete!"
    print_info "Commands and agent are now available for all your projects."
}

# Function to show what will be installed
show_files() {
    print_info "The following files will be installed:"
    print_info "Source location: $SCRIPT_DIR"
    echo ""
    echo "Commands:"
    for file in "$SCRIPT_DIR/commands"/*.md; do
        if [ -f "$file" ]; then
            echo "  - $(basename "$file")"
        fi
    done
    echo ""
    echo "Agents:"
    if [ -f "$SCRIPT_DIR/agent__gemini-analyzer.md" ]; then
        echo "  - gemini-analyzer.md"
    fi
    echo ""
}

# Main installation function
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} Gemini MCP Claude Configuration Installer                  ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check if source files exist
    print_info "Checking source files..."
    check_source_files
    print_success "All required files found"
    echo ""

    # Show what will be installed
    show_files

    # Ask for installation type
    echo -e "${YELLOW}Choose installation type:${NC}"
    echo "  1) Local (project-specific) - installs to ./.claude/"
    echo "  2) Global (user-wide) - installs to ~/.claude/"
    echo "  3) Cancel"
    echo ""

    while true; do
        read -p "Enter your choice (1-3): " choice
        case $choice in
            1)
                install_local
                break
                ;;
            2)
                install_global
                break
                ;;
            3)
                print_info "Installation cancelled."
                exit 0
                ;;
            *)
                print_warning "Invalid choice. Please enter 1, 2, or 3."
                ;;
        esac
    done

    echo ""
    print_info "Next steps:"
    echo "  1. Ensure the Gemini MCP server is configured:"
    echo "     claude mcp add gemini-mcp uv run $SCRIPT_DIR/src/gemini_mcp/__init__.py"
    echo "  2. Try the new commands:"
    echo "     /gemini-overview"
    echo "     /gemini-analyze src/"
    echo "  3. Or use the agent:"
    echo "     /agents gemini-analyzer"
    echo ""
    print_success "Happy analyzing! 🚀"
}

# Run the script
main "$@"