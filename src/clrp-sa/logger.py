#!/usr/bin/env python3

from typing import List
from pathlib import Path


class Logger:
    """A simple Logger with hierarchical indentation support"""

    def __init__(self, name: str, log_output: bool = False) -> None:
        self.name: str = name
        self.logs: List[str] = []
        self.log_output: bool = log_output
        self.indent_level: int = 0
        self.indent_char: str = "  "

    def log(self, msg: str) -> None:
        """Logs a message with a specified indentation level"""

        if not self.log_output:
            return

        indent = self.indent_char * self.indent_level
        self.logs.append(f"{indent}{msg}")

    def increase_indent(self) -> None:
        """Increases the indentation level for nested logging"""
        self.indent_level += 1

    def flush(self) -> None:
        self.logs = []

    def decrease_indent(self) -> None:
        """Decreases the indentation level for nested logging"""
        self.indent_level = max(0, self.indent_level - 1)

    def print_logs_to_file(self) -> None:
        """Writes all logged messages to a file"""
        if not self.log_output:
            return

        file_path = Path(self.name + ".txt")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open(mode='w', encoding='utf-8') as file:
            file.write("\n".join(self.logs))
