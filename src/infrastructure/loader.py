from src.infrastructure.logger import log
from typing import List, Type, Optional
from src.core.base import NoxBot
from pathlib import Path
import importlib.util
import ast
import sys


class BotLoader:
    """Lightweight loader for custom bots."""
    def __init__(self, path: str = "data/bots"):
        self.bots_dir = Path(path)
        self.bots_dir.mkdir(parents=True, exist_ok=True)
        log.info(f"initialized BotLoader(path={path}) successfully")

    def _is_bot_using_base(self, path: Path, base_class_name: str) -> Optional[str]:
        """
        Analyzes the bot without importing it.

        :param path: the path to the file
        :param base_class_name: name of the base class
        """
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if (isinstance(base, ast.Name) and base.id == base_class_name) or \
                                (isinstance(base, ast.Attribute) and base.attr == base_class_name):
                            return node.name

            return None
        except Exception as e:
            log.exception(f"Failed to parse {path}: {e}")
            return None

    def search_bots(self, base_class_name: str = "NoxBot") -> List[dict]:
        """
        Performs a quick search for custom bots.

        :param base_class_name: name of the base class
        """
        discovered = []

        for path in self.bots_dir.rglob("*.py"):
            if path.name == "__init__.py" or not path.is_file():
                continue

            class_name = self._is_bot_using_base(path, base_class_name)
            if class_name:
                discovered.append({
                    "path": path,
                    "class_name": class_name,
                    "module_name": path.stem
                })

        return discovered

    def import_bot(self, bot_info: Optional[dict]) -> Optional[Type[NoxBot]]:
        """
        Imports the required bot.
        :param bot_info: dictionary with bot data
        """
        try:
            spec = importlib.util.spec_from_file_location(bot_info["module_name"], bot_info["path"])
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[bot_info["module_name"]] = module
                spec.loader.exec_module(module)
                return getattr(module, bot_info["class_name"])
        except Exception as e:
            log.exception(f"Failed to import bot {bot_info['class_name']}: {e}")

        return None
