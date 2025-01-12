# nexus-ai/nexus_ai/utils/config.py
import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".nexus-ai"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Load keys in order of precedence
        self._load_api_keys()

    def _load_api_keys(self):
        """Load API keys from various sources"""
        # 1. Try environment variables first
        if not os.getenv("ANTHROPIC_API_KEY"):
            # 2. Try project .env
            load_dotenv()

            # 3. Try ~/.api_keys
            api_keys_file = Path.home() / ".api_keys"
            if api_keys_file.exists():
                load_dotenv(api_keys_file)

            # 4. Try ~/.taskagent/config
            config_file = self.config_dir / "config"
            if config_file.exists():
                load_dotenv(config_file)

    @staticmethod
    def setup_api_keys():
        """Interactive setup for API keys"""
        key = input("Enter your Anthropic API key: ")

        # Ask user where to save
        print("\nWhere would you like to save your API key?")
        print("1. ~/.api_keys (recommended for general use)")
        print("2. Project .env (recommended for project-specific)")
        print("3. ~/.taskagent/config")

        choice = input("Choose (1-3): ")

        if choice == "1":
            path = Path.home() / ".api_keys"
        elif choice == "2":
            path = Path.cwd() / ".env"
        else:
            path = Path.home() / ".taskagent" / "config"

        # Create or append to file
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            with open(path, "a") as f:
                f.write(f"\nANTHROPIC_API_KEY='{key}'\n")
        else:
            with open(path, "w") as f:
                f.write(f"ANTHROPIC_API_KEY='{key}'\n")

        # Set permissions
        path.chmod(0o600)

        print(f"\nAPI key saved to {path}")
        if choice == "1":
            print("\nTo load automatically, add this to your ~/.bashrc or ~/.zshrc:")
            print(f"source {path}")
