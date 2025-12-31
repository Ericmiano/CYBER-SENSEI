# backend/app/engines/lab.py
import os
import logging
import subprocess
import json
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class LabManager:
    """Manages cybersecurity lab environments with Docker integration."""
    
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
            "docker_image": "alpine:latest",
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
            "docker_image": "cyberxsecurity/dvwa",
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
            "docker_image": "ubuntu:22.04",
            "commands": ["bash", "ls", "cd", "cat", "grep", "find"],
        },
    }
    
    _active_labs: Dict[str, Dict] = {}  # Track active lab containers
    
    def __init__(self):
        """Initialize the lab manager."""
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.labs_dir = self.data_dir / "labs"
        self.labs_dir.mkdir(parents=True, exist_ok=True)
    
    def _check_docker_available(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _get_container_name(self, lab_id: str, user_id: Optional[str] = None) -> str:
        """Generate a unique container name."""
        if user_id:
            return f"cyber-sensei-{lab_id}-{user_id}"
        return f"cyber-sensei-{lab_id}"
    
    def start_lab(self, lab_name: str, user_id: Optional[str] = None) -> str:
        """Starts a predefined lab environment using Docker."""
        if lab_name not in self._LAB_LIBRARY:
            return f"Error: Lab '{lab_name}' is not registered."
        
        if not self._check_docker_available():
            logger.warning("Docker not available, returning instructions only")
            lab_info = self._LAB_LIBRARY[lab_name]
            return (
                f"Lab '{lab_name}' instructions:\n"
                f"Objective: {lab_info['objective']}\n"
                f"Steps:\n" + "\n".join(f"  {i+1}. {step}" for i, step in enumerate(lab_info['steps']))
            )
        
        lab_info = self._LAB_LIBRARY[lab_name]
        container_name = self._get_container_name(lab_name, user_id)
        
        # Check if container already exists
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if container_name in result.stdout:
                # Container exists, start it
                subprocess.run(
                    ["docker", "start", container_name],
                    capture_output=True,
                    timeout=30
                )
                self._active_labs[lab_name] = {"container": container_name, "status": "running"}
                return f"Lab '{lab_name}' container started. Container: {container_name}"
        except Exception as e:
            logger.error(f"Error checking container: {e}")
        
        # Create and start new container
        try:
            docker_image = lab_info.get("docker_image", "alpine:latest")
            
            # Pull image if needed
            subprocess.run(
                ["docker", "pull", docker_image],
                capture_output=True,
                timeout=300
            )
            
            # Run container
            cmd = [
                "docker", "run", "-d",
                "--name", container_name,
                "--rm",
                docker_image,
                "tail", "-f", "/dev/null"  # Keep container running
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self._active_labs[lab_name] = {"container": container_name, "status": "running"}
                return (
                    f"Lab '{lab_name}' started successfully!\n"
                    f"Container: {container_name}\n"
                    f"Objective: {lab_info['objective']}\n"
                    f"Use 'docker exec -it {container_name} /bin/sh' to access the lab environment."
                )
            else:
                return f"Error starting lab: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return f"Error: Timeout while starting lab '{lab_name}'"
        except Exception as e:
            logger.error(f"Error starting lab: {e}")
            return f"Error starting lab '{lab_name}': {str(e)}"
    
    def stop_lab(self, lab_name: str, user_id: Optional[str] = None) -> str:
        """Stops a lab environment."""
        if not self._check_docker_available():
            return "Docker not available. Cannot stop lab."
        
        container_name = self._get_container_name(lab_name, user_id)
        
        try:
            result = subprocess.run(
                ["docker", "stop", container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                if lab_name in self._active_labs:
                    del self._active_labs[lab_name]
                return f"Lab '{lab_name}' stopped successfully."
            else:
                return f"Error stopping lab: {result.stderr}"
        except Exception as e:
            logger.error(f"Error stopping lab: {e}")
            return f"Error stopping lab '{lab_name}': {str(e)}"
    
    def get_lab_instructions(self, lab_id: str) -> Optional[Dict]:
        """Get instructions for a lab."""
        lab = self._LAB_LIBRARY.get(lab_id)
        if not lab:
            return None
        
        container_name = self._get_container_name(lab_id)
        is_running = False
        
        if self._check_docker_available():
            try:
                result = subprocess.run(
                    ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                is_running = container_name in result.stdout
            except Exception:
                pass
        
        return {
            "lab_id": lab_id,
            "title": lab["title"],
            "objective": lab["objective"],
            "steps": lab["steps"],
            "expected_duration": lab["expected_duration"],
            "is_running": is_running,
            "container_name": container_name if is_running else None,
        }
    
    def execute_command(self, lab_id: str, command: str, user_id: Optional[str] = None) -> str:
        """Execute a command in a lab environment."""
        if lab_id not in self._LAB_LIBRARY:
            return f"Error: Lab '{lab_id}' is not registered."
        
        if not self._check_docker_available():
            # Simulate command execution for testing
            lab_info = self._LAB_LIBRARY[lab_id]
            allowed_commands = lab_info.get("commands", [])
            cmd_base = command.split()[0] if command else ""
            
            if cmd_base in allowed_commands:
                return f"Simulated output for '{command}' in lab '{lab_id}':\nCommand executed successfully."
            else:
                return f"Warning: Command '{cmd_base}' not in allowed list for this lab."
        
        container_name = self._get_container_name(lab_id, user_id)
        
        # Check if container is running
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if container_name not in result.stdout:
                return f"Error: Lab container '{container_name}' is not running. Start the lab first."
        except Exception as e:
            logger.error(f"Error checking container status: {e}")
            return f"Error: Could not check container status."
        
        # Execute command in container
        try:
            # Security: Only allow safe commands
            lab_info = self._LAB_LIBRARY[lab_id]
            allowed_commands = lab_info.get("commands", [])
            cmd_base = command.split()[0] if command else ""
            
            if allowed_commands and cmd_base not in allowed_commands:
                return f"Error: Command '{cmd_base}' is not allowed in this lab environment."
            
            result = subprocess.run(
                ["docker", "exec", container_name, "sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout if result.stdout else "Command executed successfully (no output)."
            else:
                return f"Error: {result.stderr}" if result.stderr else "Command failed."
                
        except subprocess.TimeoutExpired:
            return "Error: Command execution timed out."
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return f"Error executing command: {str(e)}"
    
    def list_active_labs(self) -> Dict[str, Dict]:
        """List all active lab environments."""
        return self._active_labs.copy()
