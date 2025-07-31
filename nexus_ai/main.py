# nexus_ai/main.py

import asyncio
import argparse
import sys
from nexus_ai.core.session import Session
from nexus_ai.repl.prompt_toolkit_repl import NexusPromptToolkitREPL
from nexus_ai.models import ModelType, ExecutionMode


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='NEXUS AI - Neural EXecution and Understanding System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nexus-ai                         # Start with Claude local (default)
  nexus-ai --model claude-local    # Start with Claude local execution
  nexus-ai --model claude-api      # Start with Claude API
  nexus-ai --model gemini-local    # Start with Gemini local execution
  nexus-ai --model gemini-api      # Start with Gemini API
  nexus-ai --session-id test       # Start with specific session ID
  nexus --help                     # Show help (same as nexus-ai)
        """
    )
    
    parser.add_argument(
        '--session-id',
        type=str,
        help='Use specific session ID'
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        choices=['claude-local', 'claude-api', 'gemini-local', 'gemini-api'],
        default='claude-local',
        help='Default AI model to use (default: claude-local)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='NEXUS AI v0.3.0'
    )
    
    return parser


def parse_model_selection(model_str: str) -> tuple[ModelType, ExecutionMode]:
    """Parse model string into ModelType and ExecutionMode"""
    if model_str == 'claude-local':
        return ModelType.CLAUDE, ExecutionMode.LOCAL
    elif model_str == 'claude-api':
        return ModelType.CLAUDE, ExecutionMode.API
    elif model_str == 'gemini-local':
        return ModelType.GEMINI, ExecutionMode.LOCAL
    elif model_str == 'gemini-api':
        return ModelType.GEMINI, ExecutionMode.API
    else:
        # Default fallback
        return ModelType.CLAUDE, ExecutionMode.LOCAL


def main():
    """Main entry point for NEXUS AI"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Parse model selection
        model_type, execution_mode = parse_model_selection(args.model)
        
        # Create session with optional session ID
        session = Session(args.session_id) if args.session_id else None
        repl = NexusPromptToolkitREPL(session, default_model=model_type, default_mode=execution_mode)
        
        # Run the REPL
        asyncio.run(repl.run())
        
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
