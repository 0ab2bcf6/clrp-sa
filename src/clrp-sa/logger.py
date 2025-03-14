#!/usr/bin/env python3

import logging
from datetime import datetime
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

        self.logger: logging.Logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        self.logger.handlers.clear()

        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def info(self, solver: str, message: str) -> None:
        indent = self.indent_char * self.indent_level
        log_message = f"{indent}{message}"
        self.logger.info(log_message)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stored_message = f"{timestamp} {indent}[INFO] {self.name}: {solver} - {message}"
        self.logs.append(stored_message)
        if self.log_output:
            print(stored_message)

    def warning(self, message: str) -> None:
        indent = self.indent_char * self.indent_level
        log_message = f"{indent}{message}"
        self.logger.warning(log_message)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stored_message = f"{timestamp} {indent}[WARNING] {self.name}: {message}"
        self.logs.append(stored_message)
        if self.log_output:
            print(stored_message)

    def error(self, message: str) -> None:
        indent = self.indent_char * self.indent_level
        log_message = f"{indent}{message}"
        self.logger.error(log_message)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stored_message = f"{timestamp} {indent}[ERROR] {self.name}: {message}"
        self.logs.append(stored_message)
        if self.log_output:
            print(stored_message)

    def log(self, msg: str) -> None:
        """Logs a message with a specified indentation level"""

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

        file_path = Path(self.name + ".txt")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open(mode='w', encoding='utf-8') as file:
            file.write("\n".join(self.logs))
