"""Port: email sending interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmailSenderPort(ABC):
    """Abstract interface for sending emails."""

    @abstractmethod
    def send(self, subject: str, html_content: str) -> bool:
        """Send an HTML email. Returns True on success."""

    @abstractmethod
    def send_error(self, error_message: str) -> bool:
        """Send an error notification email. Returns True on success."""
