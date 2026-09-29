import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EventWriter:
    """Writes events to a JSONL file."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = None

    def open(self):
        """Open the file for appending."""
        self._file = open(self.file_path, "a", encoding="utf-8")

    def write(self, event: Dict[str, Any]):
        """Write a single event to the JSONL file."""
        if not self._file:
            self.open()
        self._file.write(json.dumps(event) + "\n")
        self._file.flush()

    def close(self):
        """Close the output file."""
        if self._file:
            self._file.close()
            self._file = None
