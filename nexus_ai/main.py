# nexus_ai/main.py

import asyncio
import argparse
import sys
from nexus_ai.core.session import Session
from nexus_ai.repl.prompt_toolkit_repl import NexusPromptToolkitREPL


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description='NEXUS AI - Neural EXecution and Understanding System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nexus-ai                    # Start NEXUS AI
  nexus-ai --session-id test  # Start with specific session ID
  nexus --help                # Show help (same as nexus-ai)
        """
    )
    
    parser.add_argument(
        '--session-id',
        type=str,
        help='Use specific session ID'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='NEXUS AI v0.2.0'
    )
    
    return parser


def main():
    """Main entry point for NEXUS AI"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Create session with optional session ID
        session = Session(args.session_id) if args.session_id else None
        repl = NexusPromptToolkitREPL(session)
        
        # Run the REPL
        asyncio.run(repl.run())
        
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
