# NEXUS - Neural EXecution and Understanding System

```markdown
███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗
████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝
██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗
██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║
██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║
╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
NEXUS is an interactive environment that combines Python REPL, Bash execution, and Claude AI assistance. It provides a seamless interface for coding, system operations, and AI-guided development.
```

## Features

- Python REPL with persistent environment
- Bash command execution
- Claude AI integration for assistance and code generation
- Multi-line code block support
- Command history and context awareness
- File system operations
- Output analysis and suggestions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Eliran79/nexus-ai.git
cd nexus-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

4. Set up your Anthropic API key:
```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Usage

Start NEXUS by running:
```bash
nexus-ai
```

### Command Prefixes

- `>` - Execute Python code (single line)
- `!` - Execute bash commands
- `??` or `claude` - Ask Claude for assistance
- No prefix - Execute bash commands directly

### Examples

1. **Python Execution**
`````python
🔮 > print("Hello")
Hello

🔮 ?? write me a python program to count from 1 to 5

Claude's response:
I'll write a simple Python program to count from 1 to 5 using a few different approaches:

1. Using a `for` loop:
```python
for i in range(1, 6):
    print(i)
```

2. Using a `while` loop:
```python
count = 1
while count <= 5:
    print(count)
    count += 1
```

Expected Output:
```
1
2
3
4
5
```

I'll execute the first version for you:

>for i in range(1, 6):
>    print(i)

The program does the following:
- Uses `range(1, 6)` to generate numbers from 1 to 5 
  - The first argument (1) is the start
  - The second argument (6) is the end (exclusive)
- Prints each number in the range

Both methods accomplish the same task of counting from 1 to 5. The `for` loop is typically more concise and Pythonic for simple counting operations like this. Would you like me to explain the code in more detail?

Detected commands:
1. [python_block] for i in range(1, 6):
    print(i)
2. [python_block] count = 1
while count <= 5:
    print(count)
    count += 1
3. [python] for i in range(1, 6):
4. [python] print(i)

Enter command number to execute (or 'all'/'none'): 1

Executing python_block command: for i in range(1, 6):
    print(i)
1
2
3
4
5
Python variables: i=5

Enter command number to execute (or 'all'/'none'): none
`````

2. **File System Operations**
`````bash
?? what are the files in my current directory?

Claude's response:
I'll help you list the files in your current directory. I'll use the bash command `ls` to do this.

```bash
!ls
```

This command will list all files and directories in the current directory, including hidden files (those starting with a dot). If you want a more detailed view, I can use additional options:

```bash
!ls -la
```
- The `-l` option provides a long listing format with details like permissions, owner, size, and modification date
- The `-a` option shows all files, including hidden files

Would you like me to execute one of these commands to show you the contents of your current directory?

Detected commands:
1. [bash] ls
2. [bash] ls -la

Enter command number to execute (or 'all'/'none'): 2

Executing bash command: ls -la
total 44
drwxr-xr-x  6 eliran eliran 4096 Jan 11 22:40 .
drwxrwxrwx 67 eliran eliran 4096 Dec 30 21:40 ..
drwxr-xr-x  7 eliran eliran 4096 Dec 30 22:08 nexus_ai
drwxr-xr-x  2 eliran eliran 4096 Jan 11 22:10 nexus_ai.egg-info
-rw-r--r--  1 eliran eliran 8375 Jan 11 23:24 README.md
-rw-r--r--  1 eliran eliran   88 Dec 30 21:35 requirements.txt
-rw-r--r--  1 eliran eliran  355 Dec 30 21:41 setup.py
drwxr-xr-x  2 eliran eliran 4096 Dec 30 21:20 tests
drwxr-xr-x  5 eliran eliran 4096 Dec 30 22:05 .venv


Enter command number to execute (or 'all'/'none'): none
`````

3. **AI Analysis**
`````bash
🔮 ?? what is the biggest file based on the output?

Claude's response:
I'll analyze the directory listing to determine the largest file. From the previous output, I see the files:

1. README.md (8375 bytes)
2. requirements.txt (88 bytes)
3. setup.py (355 bytes)

The README.md is the largest file at 8,375 bytes. 

To confirm this and get a more precise view sorted by file size, I'll use the `ls` command with size sorting:

```bash
!ls -lSh
```

This command will:
- `-l`: Use long listing format
- `-S`: Sort by file size (largest first)
- `-h`: Use human-readable file sizes

Would you like me to execute this command to verify the file sizes?

Detected commands:
1. [bash] ls -lSh

Enter command number to execute (or 'all'/'none'): none
`````

### Advanced Features

1. **Python Code Blocks**
- Use ```python marks for multi-line code
- Variables persist between executions
- Full Python environment access

2. **Command Execution**
- Single commands or multiple steps
- Output capture and analysis
- Error handling and suggestions

3. **Context Awareness**
- Maintains Python environment state
- Tracks command history
- Analyzes outputs for insights

## Development

NEXUS uses a modular architecture with clear separation of concerns:
- Core REPL functionality
- Python execution engine
- Bash command handling
- Claude integration
- Session management

To contribute:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Dependencies

- Python 3.x
- Anthropic Claude API
- Required Python packages in `requirements.txt`

## License

MIT License

## Documents

- [LLM API Cost Optimization Through Orchestrator-Based Task Distribution](docs/llm_api_cost_optimization.md)

## Contributing

Contributions to NEXUS are welcomed! Here's how you can help:

### Getting Started

1. Fork the repository
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Maintain comprehensive docstrings
- Add type hints to new functions
- Keep functions focused and modular
- Add tests for new features

### Adding Features

1. **Core Functionality**
   - Extend base REPL capabilities
   - Enhance Python/Bash execution
   - Improve Claude integration

2. **User Experience**
   - Add new command types
   - Improve error messages
   - Enhance output formatting

3. **Documentation**
   - Update README.md
   - Add docstrings
   - Create usage examples

### Testing

Run tests before submitting:
```bash
pytest tests/
```

### Submitting Changes

1. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
2. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
3. Create a Pull Request
4. Describe your changes in detail
5. Reference any related issues

### Code Review Process

1. All contributions require review
2. Address review feedback
3. Keep PRs focused and manageable
4. Ensure tests pass
5. Update documentation as needed

### Need Help?

- Open an issue for bugs or suggestions
- Ask questions in Discussions
- Join our community Discord/Slack

We appreciate your interest in improving NEXUS!