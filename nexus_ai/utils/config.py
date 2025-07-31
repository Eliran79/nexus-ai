# nexus-ai/nexus_ai/utils/config.py
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional


class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".nexus-ai"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        # Load keys in order of precedence
        self._load_api_keys()
        
        # Load model preferences
        self.model_config = self._load_model_config()
    
    def _load_model_config(self) -> Dict[str, Any]:
        """Load model configuration from JSON file"""
        default_config = {
            "default_model": "claude",  # Claude is the default
            "default_execution_mode": "local",  # Local execution is the default
            "model_preferences": {
                "claude": {
                    "preferred_mode": "local",
                    "fallback_mode": "api"
                },
                "gemini": {
                    "preferred_mode": "local",
                    "fallback_mode": None
                }
            },
            "auto_fallback": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except (json.JSONDecodeError, IOError):
                # If config is corrupted, use defaults
                pass
        
        # Save default config
        self._save_model_config(default_config)
        return default_config
    
    def _save_model_config(self, config: Dict[str, Any]):
        """Save model configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config: {e}")
    
    def get_default_model(self) -> str:
        """Get the default model name"""
        return self.model_config.get("default_model", "claude")
    
    def get_default_execution_mode(self) -> str:
        """Get the default execution mode"""
        return self.model_config.get("default_execution_mode", "local")
    
    def set_default_model(self, model: str):
        """Set the default model"""
        self.model_config["default_model"] = model
        self._save_model_config(self.model_config)
    
    def set_default_execution_mode(self, mode: str):
        """Set the default execution mode"""
        self.model_config["default_execution_mode"] = mode
        self._save_model_config(self.model_config)
    
    def get_model_preferences(self, model: str) -> Dict[str, Any]:
        """Get preferences for a specific model"""
        return self.model_config.get("model_preferences", {}).get(model, {})
    
    def set_model_preference(self, model: str, key: str, value: Any):
        """Set a preference for a specific model"""
        if "model_preferences" not in self.model_config:
            self.model_config["model_preferences"] = {}
        if model not in self.model_config["model_preferences"]:
            self.model_config["model_preferences"][model] = {}
        
        self.model_config["model_preferences"][model][key] = value
        self._save_model_config(self.model_config)
    
    def get_auto_fallback(self) -> bool:
        """Get auto fallback setting"""
        return self.model_config.get("auto_fallback", True)
    
    def set_auto_fallback(self, enabled: bool):
        """Set auto fallback setting"""
        self.model_config["auto_fallback"] = enabled
        self._save_model_config(self.model_config)

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

            # 4. Try ~/.nexus-ai/config
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
            path = Path.home() / ".nexus-ai" / "config"

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
    
    def setup_model_preferences(self):
        """Interactive setup for model preferences"""
        print("\nModel Preference Setup")
        print("======================\n")
        
        # Default model
        print("Available models: claude, gemini")
        default_model = input("Default model [claude]: ").strip() or "claude"
        self.set_default_model(default_model)
        
        # Default execution mode
        print("\nExecution modes: local, api")
        default_mode = input("Default execution mode [local]: ").strip() or "local"
        self.set_default_execution_mode(default_mode)
        
        # Auto fallback
        fallback = input("\nEnable auto fallback to API if local fails? [y/N]: ").strip().lower()
        self.set_auto_fallback(fallback in ['y', 'yes'])
        
        print(f"\nModel preferences saved to {self.config_file}")
        print("\nCurrent configuration:")
        print(f"  Default model: {self.get_default_model()}")
        print(f"  Default mode: {self.get_default_execution_mode()}")
        print(f"  Auto fallback: {self.get_auto_fallback()}")
