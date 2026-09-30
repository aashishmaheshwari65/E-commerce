import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class EventReader(ABC):
    """Abstract interface for reading real-time events.
    This enables seamless integration of Kafka later."""
    
    @abstractmethod
    def read_events(self) -> Iterator[Tuple[str, Dict[str, Any]]]:
        """Yields (checkpoint_marker, event_dict)"""
        pass

    @abstractmethod
    def commit_checkpoint(self, checkpoint_marker: str):
        """Save the checkpoint to persistent storage."""
        pass

class FileEventReader(EventReader):
    """Reads events from a JSON Lines file, tailing it and preserving state via a checkpoint."""
    
    def __init__(self, file_path: Path, checkpoint_file: Path):
        self.file_path = file_path
        self.checkpoint_file = checkpoint_file
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_offset = self._load_checkpoint()

    def _load_checkpoint(self) -> int:
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    return data.get('offset', 0)
            except Exception as e:
                logger.error(f"Failed to read checkpoint: {e}. Starting from 0.")
        return 0

    def commit_checkpoint(self, checkpoint_marker: str):
        try:
            offset = int(checkpoint_marker)
            # Atomic save by writing to temp and renaming
            temp_file = self.checkpoint_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump({'offset': offset}, f)
            temp_file.replace(self.checkpoint_file)
            self.current_offset = offset
        except Exception as e:
            logger.error(f"Failed to commit checkpoint: {e}")

    def read_events(self) -> Iterator[Tuple[str, Dict[str, Any]]]:
        if not self.file_path.exists():
            logger.warning(f"File {self.file_path} does not exist yet. Waiting...")
            return

        with open(self.file_path, 'r', encoding='utf-8') as f:
            f.seek(self.current_offset)
            while True:
                line = f.readline()
                if not line:
                    break # EOF reached
                
                # We have a line, let's process it
                new_offset = f.tell()
                if not line.strip():
                    self.current_offset = new_offset
                    continue
                
                try:
                    event = json.loads(line)
                    yield str(new_offset), event
                except json.JSONDecodeError:
                    logger.error(f"Malformed JSON at offset {self.current_offset}: {line.strip()}")
                
                # Advance offset marker even if parsing fails to avoid poison pills
                self.current_offset = new_offset
