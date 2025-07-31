# NEXUS AI - Neural EXecution and Understanding System

```
███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

NEXUS AI is an interactive environment that combines Python REPL, Bash execution, and **multi-model AI assistance** with **full interactive command support**. It provides a seamless interface for coding, system operations, and AI-guided development with **local Claude execution by default** to avoid API costs.

## 🚀 What's New (v0.3.0)

### 🤖 **NEW: Multi-Model Local Execution (Claude Default)**
- **Local Claude Default**: `claude`, `??` commands now use local execution by default
- **Zero API Costs**: All Claude queries are free and private by default
- **Local Gemini**: `gemini -p <query>` - Zero API costs, full privacy  
- **Model Management**: Switch between models and execution modes
- **Auto-fallback**: Seamless fallback from local to API when needed
- **Backward Compatible**: All existing commands still work but now use local by default

### ✨ Unified Modern REPL Experience
- **Interactive Commands Fixed!** - SSH, Docker, Git, yay with proper prompts
- **Real-time Output** - See command output as it happens
- **Smart Auto-completion** - Tab completion for commands, Python, and AI models
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
- **For local execution**: `claude` and `gemini` commands installed (recommended)
- **For API mode**: Anthropic API key (optional fallback)

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

3. **Set up API key (optional for local mode):**
```bash
export ANTHROPIC_API_KEY='your-api-key-here'  # Only needed for API fallback
```

4. **Install local AI commands (recommended):**
```bash
# Install Claude Code for local Claude execution
curl -fsSL https://claude.ai/install.sh | sh

# Install Gemini CLI for local Gemini execution  
npm install -g @google-ai/generativelanguage
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

#### 🤖 AI Model Commands
| Command | Description | Example |
|---------|-------------|---------|
| `> <code>` | Execute Python code | `> print("Hello World")` |
| `! <command>` | Bash command (auto-detect mode) | `! ls -la` |
| `!i <command>` | Force interactive bash | `!i ssh user@server` |
| `!c <command>` | Force captured bash | `!c ps aux \| grep python` |
| `claude -p <query>` | **Local Claude** (no API costs) | `claude -p how do I list files recursively?` |
| `gemini -p <query>` | **Local Gemini** (no API costs) | `gemini -p explain this Python code` |
| `claude <query>` | **Local Claude** (default) | `claude explain this error` |
| `gemini <query>` | Gemini via API | `gemini what is machine learning?` |
| `?? <query>` | **Local Claude** (default) | `?? how do I debug this?` |
| `model status` | Show model configuration | `model status` |
| `model set <model>` | Set default model | `model set gemini` |
| `model mode <mode>` | Set execution mode | `model mode local` |

#### 💻 System Commands
| Command | Description | Example |
|---------|-------------|---------|
| `task: <description>` | Start new task with Claude | `task: setup a web server` |
| `help` | Show all commands | `help` |
| `exit` or `quit` | Exit NEXUS | `exit` |

### Examples

#### 0. **NEW: Multi-Model AI Commands**
```bash
# Local execution (no API costs, full privacy)
🔮 claude -p What is the difference between lists and tuples in Python?
Claude-Local response:
Lists are mutable (changeable) while tuples are immutable (unchangeable).
Lists use square brackets [], tuples use parentheses ().

🔮 gemini -p How do I reverse a string in Python?
Gemini-Local response:  
You can reverse a string using slicing: my_string[::-1]

# Model management
🔮 model status
Current Model Settings:
  Default Model: claude
  Default Mode: local

Model Availability:
  claude:
    local: ✓
    api: ✓
  gemini:
    local: ✓
    api: ✗

🔮 model set gemini        # Switch default to Gemini
Default model set to: gemini

🔮 model mode api          # Switch to API mode
Default execution mode set to: api

# Mixed usage - use different models for different tasks
🔮 claude -p Debug this Python error: NameError
🔮 gemini -p Explain machine learning in simple terms
🔮 claude explain the git workflow    # API fallback
```

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

#### 3. AI-Assisted Python Development
```bash
🔮 > import pandas as pd
🔮 > df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
🔮 > df.head()
    name  age
0  Alice   25
1    Bob   30

🔮 claude -p how do I save this dataframe to CSV?
Claude-Local response:
To save your DataFrame to a CSV file, use the `to_csv()` method:

> df.to_csv('data.csv', index=False)

This will save your DataFrame to 'data.csv' without the row indices.
```

#### 4. System Administration
```bash
🔮 !c ps aux | grep python     # Captured output for analysis
PID   USER   %CPU %MEM    VSZ   RSS TTY   STAT START   TIME COMMAND
1234  user    2.1  1.5  45000 15000 pts/1  S+   10:30   0:05 python nexus.py

🔮 gemini -p analyze the process output above
Gemini-Local response:
Based on the process output, I can see:
- Process ID: 1234
- CPU usage: 2.1%
- Memory usage: 1.5%
- The process is running nexus.py
- It's been running since 10:30 for 5 seconds
...
```

#### 5. Multi-Model Development Workflow
```bash
# Use different models for different strengths
🔮 claude -p Create a Python function to validate email addresses
Claude-Local response:
[Detailed implementation with regex and validation logic]

🔮 gemini -p Explain the email validation function above
Gemini-Local response: 
[Clear explanation of how the validation works]

🔮 claude -p Write unit tests for this email validator
Claude-Local response:
[Comprehensive test cases with pytest]
```

#### 6. Original Development Workflow
```bash
🔮 task: create a simple web API using FastAPI

AI Assistant response (using default model):
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
# Optional (only needed for API fallback)
export ANTHROPIC_API_KEY="your-api-key"

# Optional customization
export NEXUS_HISTORY_FILE="~/.nexus_history"  # Command history location
export NEXUS_MAX_HISTORY="1000"               # Max history entries
```

### Model Configuration
```bash
# Interactive model setup
nexus-ai
🔮 model status           # Check current configuration
🔮 model set claude       # Set default model
🔮 model mode local       # Set default to local execution

# Configuration is saved to ~/.nexus-ai/config.json
```

### Customization
The enhanced REPL supports:
- Custom key bindings
- Color scheme customization
- Toolbar configuration
- Auto-completion settings

## Troubleshooting

### Common Issues

**Q: "Model unavailable" errors**  
A: Install local AI commands:
- Claude: `curl -fsSL https://claude.ai/install.sh | sh`
- Gemini: Check if `gemini` command is available
- Fallback: Set `ANTHROPIC_API_KEY` for API mode

**Q: Interactive commands like yay don't work properly**
A: This has been fixed in v0.2.0! All interactive commands now work with proper terminal emulation.

**Q: "Command not found: nexus"**
A: Run `pip install -e .` from the project directory

**Q: Claude API errors**
A: Use local mode with `claude -p` or check your `ANTHROPIC_API_KEY` environment variable

**Q: Python commands not persisting**
A: Variables persist within a session. Use `> globals()` to see current variables

**Q: Which model should I use?**
A: Both models work great locally! Try both and see which you prefer:
- Claude: Generally excellent for coding and analysis
- Gemini: Great for explanations and creative tasks

### Getting Help
- Use `help` command in NEXUS to see all available commands
- Check model status with `model status`
- Test with `claude -p hello` or `gemini -p hello`
- Check command with `claude -p explain command syntax`
- Open GitHub issues for bugs
- Use `!i` prefix for commands that need interaction

## Development

### Architecture
- **Core REPL**: `nexus_ai/repl/prompt_toolkit_repl.py` - Modern REPL with terminal emulation
- **Executor**: `nexus_ai/core/executor.py` - PTY-based subprocess handling  
- **Model System**: `nexus_ai/models/` - Multi-model abstraction layer
  - `base.py` - Model interface and enums
  - `claude_local.py` - Local Claude execution
  - `gemini_local.py` - Local Gemini execution
  - `claude_api.py` - Claude API fallback
  - `factory.py` - Model factory and switching
- **Legacy Claude**: `nexus_ai/claude/client.py` - Backward compatibility
- **Configuration**: `nexus_ai/utils/config.py` - Model preferences and settings
- **Session**: `nexus_ai/core/session.py` - State management
- **Main Entry**: `nexus_ai/main.py` - Unified command-line interface

### Testing
```bash
# Run comprehensive tests
python tests/test_nexus.py
python tests/test_pty_fix.py
python tests/test_new_features.py    # Multi-model tests

# Test model functionality
python demo_multi_model_upgrade.py   # Interactive demo

# Test specific functionality
python -c "
import asyncio
from nexus_ai.repl.prompt_toolkit_repl import NexusPromptToolkitREPL
repl = NexusPromptToolkitREPL()
print('✓ NEXUS loads successfully')
"

# Test model availability
python -c "
from nexus_ai.models import model_factory
print('Model availability:', model_factory.get_available_models())
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

## Recent Improvements (v0.3.0)

### ✅ **NEW: Multi-Model Local Execution**
- **Local Claude**: Execute `claude -p` commands without API costs
- **Local Gemini**: Execute `gemini -p` commands without API costs
- **Model Management**: `model status`, `model set`, `model mode` commands
- **Auto-fallback**: Seamless fallback from local to API when needed
- **Privacy**: All local execution, no data sent to external APIs
- **Speed**: Faster responses with no network latency
- **Configuration**: Model preferences saved to `~/.nexus-ai/config.json`

### ✅ Complete Interactive Command Fix
- **Terminal emulation**: Proper PTY support for all interactive commands
- **AUR helpers**: `yay`, `pacman`, `paru` work perfectly with package selection
- **Password prompts**: SSH, sudo, and other authentication prompts visible
- **Container interaction**: Docker containers with proper TTY allocation
- **Editor integration**: Git commit, vim, nano launch correctly

### ✅ Enhanced Architecture  
- **Unified commands**: Both `nexus` and `nexus-ai` use the same modern interface
- **Model abstraction**: Clean separation between local and API execution
- **Extensible design**: Easy to add new models and execution modes
- **Backward compatibility**: All existing commands continue to work
- **Better testing**: Comprehensive test suite for all features
- **Enhanced UX**: Auto-completion for model commands, syntax highlighting, persistent history

## Dependencies

### Core Dependencies
- **Python 3.8+** (tested through 3.13)
- **prompt_toolkit** - Enhanced terminal interface
- **pygments** - Syntax highlighting
- **python-dotenv** - Environment variable loading

### AI Model Dependencies
- **anthropic** - Claude API client (for API fallback)
- **claude** command - Local Claude execution (install via claude.ai)
- **gemini** command - Local Gemini execution

### Optional Dependencies
```bash
# For Gemini API support (future)
pip install nexus-ai[gemini-api]

# For all optional features
pip install nexus-ai[all]
```

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for enhanced terminal experience
- Powered by [Anthropic's Claude](https://www.anthropic.com/) for AI assistance
- Inspired by IPython and modern REPL design principles

---

**Happy coding with NEXUS AI! 🚀**