import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class StreamingJSONParser:
    """Handles streaming JSON parsing with buffering."""

    def __init__(self):
        """Initialize parser with empty buffer."""
        self.buffer = ""

    def process_chunk(self, content: str) -> list[dict]:
        """
        Process incoming content and yield complete JSON objects.
        """
        self.buffer += content
        events = []

        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            line = line.strip()

            if not line:
                continue

            event = self._parse_line(line)
            if event:
                events.append(event)

        return events

    def _parse_line(self, line: str) -> Optional[dict]:
        """Parse a single line as JSON."""
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            logger.warning(f"Incomplete JSON line skipped: {line[:100]}")
            return None

    def reset(self) -> None:
        """Reset the buffer."""
        self.buffer = ""

    def flush(self) -> list[dict]:
        """Parse any remaining buffered JSON."""
        events = []
        remaining = self.buffer.strip()

        if remaining:
            try:
                event = json.loads(remaining)
                events.append(event)
            except json.JSONDecodeError:
                logger.warning(f"Unparseable trailing buffer: {remaining[:100]}")

        self.reset()
        return events

    def has_buffered_data(self) -> bool:
        """Check if there's unparsed data in buffer."""
        return bool(self.buffer.strip())
