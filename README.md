# NEXUS AI - Neural EXecution and Understanding System

```
███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

NEXUS AI is an interactive environment that combines Python REPL, Bash execution, and Claude AI assistance with **full interactive command support**. It provides a seamless interface for coding, system operations, and AI-guided development.

## 🚀 What's New (v0.2.0)

### ✨ Unified Modern REPL Experience
- **Interactive Commands Fixed!** - SSH, Docker, Git, yay with proper prompts
- **Real-time Output** - See command output as it happens
- **Smart Auto-completion** - Tab completion for commands and Python
- **Syntax Highlighting** - Beautiful code highlighting
- **Command History** - Navigate with Up/Down arrows
- **Background Processes** - Launch VSCode without blocking
- **Simplified Commands** - Both `nexus` and `nexus-ai` use the same modern interface

### 🎯 Solved: Terminal Input Issues
Interactive commands including AUR helpers like `yay` now work perfectly with proper terminal emulation:

```bash
🔮 !ssh user@server            # SSH with visible password prompts
🔮 !docker run -it ubuntu      # Interactive containers work
🔮 !git commit                 # Editor launches properly
🔮 !yay -Syu                   # AUR helper with package selection
🔮 !sudo apt update            # Y/n prompts visible
🔮 !code .                     # VSCode opens, prompt returns
```

## Features

### Core Capabilities
- **Python REPL** with persistent environment and real-time execution
- **Bash Command Execution** with smart interactive/captured mode detection  
- **Claude AI Integration** for assistance, code generation, and analysis
- **Multi-line Code Support** with proper indentation handling
- **Session Management** with command history and context awareness
- **File System Operations** with full path and permission support

### Enhanced User Experience
- **Auto-completion** for NEXUS commands, Python keywords, and bash commands
- **Syntax highlighting** with custom color schemes
- **Real-time output streaming** for long-running commands
- **Bottom toolbar** showing session information
- **Multi-line input support** for complex code blocks
- **Command history persistence** across sessions

### Smart Command Handling
- **Auto-detection** of interactive vs captured commands
- **Force modes**: `!i` (interactive), `!c` (captured)
- **Background execution** for editors and GUI applications
- **Timeout handling** and error recovery
- **Real-time output** for monitoring progress

## Installation

### Prerequisites
- Python 3.8+ (tested up to Python 3.13)
- Anthropic API key

### Quick Install

1. **Clone the repository:**
```bash
git clone https://github.com/Eliran79/nexus-ai.git
cd nexus-ai
```

2. **Install using pip:**
```bash
pip install -e .
```

3. **Set up your Anthropic API key:**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

### Development Install

```bash
# Clone and enter directory
git clone https://github.com/Eliran79/nexus-ai.git
cd nexus-ai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

## Usage

### Starting NEXUS

**Start NEXUS AI (Both commands work identically):**
```bash
nexus                    # Start NEXUS AI
nexus-ai                 # Same as above
```

**Command options:**
```bash
nexus --help             # Show help and options
nexus --session-id test  # Start with specific session ID
nexus --version          # Show version information
```

### Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `> <code>` | Execute Python code | `> print("Hello World")` |
| `! <command>` | Bash command (auto-detect mode) | `! ls -la` |
| `!i <command>` | Force interactive bash | `!i ssh user@server` |
| `!c <command>` | Force captured bash | `!c ps aux \| grep python` |
| `?? <query>` | Ask Claude for help | `?? how do I list files recursively?` |
| `claude <query>` | Alternative Claude syntax | `claude explain this error` |
| `task: <description>` | Start new task with Claude | `task: setup a web server` |
| `help` | Show all commands | `help` |
| `exit` or `quit` | Exit NEXUS | `exit` |

### Examples

#### 1. Interactive Commands (Now Working!)
```bash
🔮 !ssh user@server
Password: [you can type here]
user@server:~$ ls
[interactive session works perfectly]

🔮 !docker run -it python:3.11
Python 3.11.0 (main, Oct 24 2022, 18:26:48)
>>> print("Hello from container!")
Hello from container!
>>> exit()

🔮 !yay -Ss firefox
:: Synchronizing package databases...
Choose packages to install (e.g. 1-3,5):
2-121
[packages install successfully]

🔮 !git commit
[editor opens for commit message]
[Esc + :wq to save and exit vim]
[main abc1234] Your commit message
 1 file changed, 5 insertions(+)
```

#### 2. Background Processes
```bash
🔮 !code .                     # VSCode opens, prompt returns immediately
✓ Launched in background: code .

🔮 !code --wait file.py        # Wait for VSCode to close
[VSCode opens, NEXUS waits until you close the file]

🔮 !firefox https://github.com # Browser opens in background
✓ Launched in background: firefox https://github.com
```

#### 3. Python Development
```bash
🔮 > import pandas as pd
🔮 > df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
🔮 > df.head()
    name  age
0  Alice   25
1    Bob   30

🔮 ?? how do I save this dataframe to CSV?
Claude's response:
To save your DataFrame to a CSV file, use the `to_csv()` method:

> df.to_csv('data.csv', index=False)

This will save your DataFrame to 'data.csv' without the row indices.
```

#### 4. System Administration
```bash
🔮 !c ps aux | grep python     # Captured output for analysis
PID   USER   %CPU %MEM    VSZ   RSS TTY   STAT START   TIME COMMAND
1234  user    2.1  1.5  45000 15000 pts/1  S+   10:30   0:05 python nexus.py

🔮 ?? analyze the process output above
Claude's response:
Based on the process output, I can see:
- Process ID: 1234
- CPU usage: 2.1%
- Memory usage: 1.5%
- The process is running nexus.py
- It's been running since 10:30 for 5 seconds
...
```

#### 5. Development Workflow
```bash
🔮 task: create a simple web API using FastAPI

Claude's response:
I'll help you create a simple FastAPI web API. Let me break this down into steps:

1. First, let's install FastAPI and uvicorn:
!pip install fastapi uvicorn

2. Create a simple API file:
> with open('main.py', 'w') as f:
>     f.write('''
> from fastapi import FastAPI
> 
> app = FastAPI()
> 
> @app.get("/")
> def read_root():
>     return {"Hello": "World"}
> 
> @app.get("/items/{item_id}")
> def read_item(item_id: int, q: str = None):
>     return {"item_id": item_id, "q": q}
> ''')

3. Run the server:
!uvicorn main:app --reload

Would you like me to execute these commands?
```

## Advanced Features

### Smart Command Detection
NEXUS automatically detects command types:

- **Interactive**: `ssh`, `docker run -it`, `git commit`, `sudo`, `vim`, `yay`, `pacman`, etc.
- **Captured**: `ls`, `cat`, `grep`, `ps`, etc. 
- **Background**: `code`, `subl`, `firefox`, `chrome`, etc.

### Session Management
- **Persistent Python environment** across commands
- **Command history** saved between sessions
- **Output history** for Claude context
- **Session metadata** tracking

### Claude Integration
- **Context-aware responses** using command history
- **Code extraction** and execution prompting
- **Error analysis** and suggestions
- **Task-oriented assistance**

## Configuration

### Environment Variables
```bash
# Required
export ANTHROPIC_API_KEY="your-api-key"

# Optional
export NEXUS_HISTORY_FILE="~/.nexus_history"  # Command history location
export NEXUS_MAX_HISTORY="1000"               # Max history entries
```

### Customization
The enhanced REPL supports:
- Custom key bindings
- Color scheme customization
- Toolbar configuration
- Auto-completion settings

## Troubleshooting

### Common Issues

**Q: Interactive commands like yay don't work properly**
A: This has been fixed in v0.2.0! All interactive commands now work with proper terminal emulation.

**Q: "Command not found: nexus"**
A: Run `pip install -e .` from the project directory

**Q: Claude API errors**
A: Check your `ANTHROPIC_API_KEY` environment variable

**Q: Python commands not persisting**
A: Variables persist within a session. Use `> globals()` to see current variables

### Getting Help
- Use `help` command in NEXUS
- Check command with `?? explain command syntax`
- Open GitHub issues for bugs
- Use `!i` prefix for commands that need interaction

## Development

### Architecture
- **Core REPL**: `nexus_ai/repl/prompt_toolkit_repl.py` - Modern REPL with terminal emulation
- **Executor**: `nexus_ai/core/executor.py` - PTY-based subprocess handling  
- **Claude Client**: `nexus_ai/claude/client.py` - AI integration
- **Session**: `nexus_ai/core/session.py` - State management
- **Main Entry**: `nexus_ai/main.py` - Unified command-line interface

### Testing
```bash
# Run comprehensive tests
python tests/test_nexus.py
python tests/test_pty_fix.py

# Test specific functionality
python -c "
import asyncio
from nexus_ai.repl.prompt_toolkit_repl import NexusPromptToolkitREPL
repl = NexusPromptToolkitREPL()
print('✓ NEXUS loads successfully')
"
```

### Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Make changes and test
5. Submit pull request

### Development Commands
```bash
# Format code
black nexus_ai/

# Type checking  
mypy nexus_ai/

# Sort imports
isort nexus_ai/

# Run tests
pytest tests/
```

## Recent Improvements (v0.2.0)

### ✅ Complete Interactive Command Fix
- **Terminal emulation**: Proper PTY support for all interactive commands
- **AUR helpers**: `yay`, `pacman`, `paru` work perfectly with package selection
- **Password prompts**: SSH, sudo, and other authentication prompts visible
- **Container interaction**: Docker containers with proper TTY allocation
- **Editor integration**: Git commit, vim, nano launch correctly

### ✅ Simplified Architecture  
- **Unified commands**: Both `nexus` and `nexus-ai` use the same modern interface
- **Clean codebase**: Removed legacy cmd.Cmd implementation
- **Better testing**: Comprehensive test suite for interactive features
- **Enhanced UX**: Auto-completion, syntax highlighting, persistent history

## Dependencies

- **Python 3.8+** (tested through 3.13)
- **anthropic** - Claude AI API client
- **prompt_toolkit** - Enhanced terminal interface
- **pygments** - Syntax highlighting
- **python-dotenv** - Environment variable loading

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for enhanced terminal experience
- Powered by [Anthropic's Claude](https://www.anthropic.com/) for AI assistance
- Inspired by IPython and modern REPL design principles

---

**Happy coding with NEXUS AI! 🚀**