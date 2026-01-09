# backend/app/engines/lab.py
import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class LabManager:
    """Manages cybersecurity lab environments without requiring Docker.

    This simplified manager returns instructions and simulates command execution
    so the project can run in environments without Docker.
    """

    _LAB_LIBRARY = {
        "network-troubleshooting": {
            "title": "Network Troubleshooting",
            "objective": "Practice network debugging commands inside a controlled range.",
            "steps": [
                "Use `ifconfig` / `ipconfig` to review interfaces.",
                "Run `ping` to verify reachability.",
                "Trace routes with `traceroute` or `tracert`.",
                "Document findings and propose mitigation steps.",
            ],
            "expected_duration": "15 minutes",
            "commands": ["ifconfig", "ping", "traceroute", "netstat", "tcpdump"],
        },
        "web-exploitation": {
            "title": "Web Exploitation Basics",
            "objective": "Identify and exploit OWASP Top 10 vulnerabilities in a sample app.",
            "steps": [
                "Run an initial reconnaissance with `nmap`.",
                "Identify SQLi vectors and capture a payload.",
                "Test stored vs reflected XSS payloads.",
                "Write a remediation report.",
            ],
            "expected_duration": "30 minutes",
            "commands": ["nmap", "curl", "sqlmap", "burpsuite"],
        },
        "linux-basics": {
            "title": "Linux Command Line Basics",
            "objective": "Learn essential Linux commands and system administration.",
            "steps": [
                "Navigate the filesystem with `cd`, `ls`, `pwd`.",
                "Manage files with `cp`, `mv`, `rm`, `chmod`.",
                "Process management with `ps`, `top`, `kill`.",
                "Network tools: `netstat`, `ss`, `iptables`.",
            ],
            "expected_duration": "20 minutes",
            "commands": ["bash", "ls", "cd", "cat", "grep", "find"],
        },
    }

    _active_labs: Dict[str, Dict] = {}

    def __init__(self):
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.labs_dir = self.data_dir / "labs"
        self.labs_dir.mkdir(parents=True, exist_ok=True)

    def start_lab(self, lab_name: str, user_id: Optional[str] = None) -> str:
        """Start a lab by returning setup instructions (no containers).

        This implementation intentionally avoids any Docker usage.
        """
        if lab_name not in self._LAB_LIBRARY:
            return f"Error: Lab '{lab_name}' is not registered."

        lab_info = self._LAB_LIBRARY[lab_name]
        lab_key = f"{lab_name}:{user_id}" if user_id else lab_name
        self._active_labs[lab_key] = {"status": "ready"}

        return (
            f"Lab '{lab_info['title']}' prepared for user '{user_id or 'anonymous'}'.\n"
            f"Objective: {lab_info['objective']}\n"
            "Steps:\n" + "\n".join(f"  {i+1}. {step}" for i, step in enumerate(lab_info['steps']))
        )

    def stop_lab(self, lab_name: str, user_id: Optional[str] = None) -> str:
        lab_key = f"{lab_name}:{user_id}" if user_id else lab_name
        if lab_key in self._active_labs:
            del self._active_labs[lab_key]
            return f"Lab '{lab_name}' stopped for user '{user_id or 'anonymous'}'."
        return f"Lab '{lab_name}' was not active."

    def get_lab_instructions(self, lab_id: str) -> Optional[Dict]:
        lab = self._LAB_LIBRARY.get(lab_id)
        if not lab:
            return None

        lab_key = lab_id
        is_running = lab_key in self._active_labs

        return {
            "lab_id": lab_id,
            "title": lab["title"],
            "objective": lab["objective"],
            "steps": lab["steps"],
            "expected_duration": lab["expected_duration"],
            "is_running": is_running,
        }

    def execute_command(self, lab_id: str, command: str, user_id: Optional[str] = None) -> str:
        """Simulate command execution and return safe, non-sensitive output.

        No system commands are run; responses are canned or simulated to keep
        behavior deterministic and safe in environments without Docker.
        """
        if lab_id not in self._LAB_LIBRARY:
            return f"Error: Lab '{lab_id}' is not registered."

        lab_info = self._LAB_LIBRARY[lab_id]
        allowed_commands = lab_info.get("commands", [])
        cmd_base = command.split()[0] if command else ""

        if cmd_base in allowed_commands:
            return f"Simulated output for '{command}' in lab '{lab_id}':\nCommand executed successfully."
        return f"Warning: Command '{cmd_base}' not allowed or cannot be executed in this environment." 

    def list_active_labs(self) -> Dict[str, Dict]:
        return self._active_labs.copy()
