import yaml
from pathlib import Path


class ConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)

    def load(self, config_name: str) -> dict:
        """Load a YAML config file by name (without extension)"""
        config_path = self.config_dir / f"{config_name}.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def list_configs(self) -> list:
        """List all available config files"""
        return [f.stem for f in self.config_dir.glob("*.yaml")]