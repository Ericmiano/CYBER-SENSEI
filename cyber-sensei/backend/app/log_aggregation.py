"""
Log aggregation setup with Elasticsearch integration.

Provides:
- Structured logging to Elasticsearch
- Log indexing and retention policies
- Kibana dashboard configuration
- Distributed tracing support
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger
from elasticsearch import Elasticsearch
import os


class StructuredLogger:
    """Logger that outputs structured JSON logs."""
    
    def __init__(self, name: str, elasticsearch_url: Optional[str] = None):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            elasticsearch_url: Elasticsearch connection URL
        """
        self.logger = logging.getLogger(name)
        self.elasticsearch_url = elasticsearch_url or os.getenv(
            "ELASTICSEARCH_URL", "http://localhost:9200"
        )
        self.es_client = None
        self.context = {}
        
        if elasticsearch_url:
            self._init_elasticsearch()
    
    def _init_elasticsearch(self):
        """Initialize Elasticsearch client."""
        try:
            self.es_client = Elasticsearch([self.elasticsearch_url])
            # Test connection
            self.es_client.info()
            logging.info("Connected to Elasticsearch")
        except Exception as e:
            logging.error(f"Failed to connect to Elasticsearch: {e}")
            self.es_client = None
    
    def set_context(self, **kwargs):
        """Set context variables to include in all logs."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear context."""
        self.context.clear()
    
    def _build_log_record(self, level: str, message: str, 
                         extra: Optional[Dict] = None) -> Dict[str, Any]:
        """Build structured log record."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "logger": self.logger.name,
            **self.context
        }
        
        if extra:
            record.update(extra)
        
        return record
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        """Log debug message."""
        record = self._build_log_record("DEBUG", message, extra)
        self.logger.debug(json.dumps(record))
        self._send_to_elasticsearch(record)
    
    def info(self, message: str, extra: Optional[Dict] = None):
        """Log info message."""
        record = self._build_log_record("INFO", message, extra)
        self.logger.info(json.dumps(record))
        self._send_to_elasticsearch(record)
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        """Log warning message."""
        record = self._build_log_record("WARNING", message, extra)
        self.logger.warning(json.dumps(record))
        self._send_to_elasticsearch(record)
    
    def error(self, message: str, extra: Optional[Dict] = None, exception: Optional[Exception] = None):
        """Log error message."""
        record = self._build_log_record("ERROR", message, extra)
        
        if exception:
            record["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": str(exception.__traceback__)
            }
        
        self.logger.error(json.dumps(record))
        self._send_to_elasticsearch(record)
    
    def critical(self, message: str, extra: Optional[Dict] = None):
        """Log critical message."""
        record = self._build_log_record("CRITICAL", message, extra)
        self.logger.critical(json.dumps(record))
        self._send_to_elasticsearch(record)
    
    def _send_to_elasticsearch(self, record: Dict[str, Any]):
        """Send log record to Elasticsearch."""
        if not self.es_client:
            return
        
        try:
            index_name = f"logs-{datetime.utcnow().strftime('%Y.%m.%d')}"
            self.es_client.index(
                index=index_name,
                document=record
            )
        except Exception as e:
            self.logger.error(f"Failed to send log to Elasticsearch: {e}")


class ElasticsearchLogHandler(logging.Handler):
    """Logging handler that sends logs to Elasticsearch."""
    
    def __init__(self, elasticsearch_url: str, index_prefix: str = "logs"):
        """
        Initialize Elasticsearch log handler.
        
        Args:
            elasticsearch_url: Elasticsearch connection URL
            index_prefix: Prefix for log indexes
        """
        super().__init__()
        self.elasticsearch_url = elasticsearch_url
        self.index_prefix = index_prefix
        self.es_client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Elasticsearch client."""
        try:
            self.es_client = Elasticsearch([self.elasticsearch_url])
            self.es_client.info()
        except Exception as e:
            logging.error(f"Failed to initialize Elasticsearch: {e}")
    
    def emit(self, record: logging.LogRecord):
        """Send log record to Elasticsearch."""
        if not self.es_client:
            return
        
        try:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            if record.exc_info:
                log_entry["exception"] = self.format(record)
            
            index_name = f"{self.index_prefix}-{datetime.utcnow().strftime('%Y.%m.%d')}"
            self.es_client.index(index=index_name, document=log_entry)
        
        except Exception:
            self.handleError(record)


class LogConfig:
    """Configure application logging with Elasticsearch integration."""
    
    @staticmethod
    def setup_logging(
        app_name: str,
        elasticsearch_url: Optional[str] = None,
        log_level: str = "INFO"
    ):
        """
        Setup comprehensive logging configuration.
        
        Args:
            app_name: Application name for logging
            elasticsearch_url: Elasticsearch URL for log aggregation
            log_level: Minimum log level to capture
        """
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level))
        
        # Console handler with JSON formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        
        # JSON formatter
        json_formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(logger)s %(message)s'
        )
        console_handler.setFormatter(json_formatter)
        
        root_logger.addHandler(console_handler)
        
        # Elasticsearch handler if URL provided
        if elasticsearch_url:
            es_handler = ElasticsearchLogHandler(elasticsearch_url, f"logs-{app_name}")
            es_handler.setLevel(getattr(logging, log_level))
            root_logger.addHandler(es_handler)
        
        logging.info(f"Logging configured for {app_name}")
    
    @staticmethod
    def get_structured_logger(name: str, elasticsearch_url: Optional[str] = None) -> StructuredLogger:
        """Get a structured logger instance."""
        return StructuredLogger(name, elasticsearch_url)


# Kibana dashboard configuration
KIBANA_DASHBOARD_CONFIG = {
    "dashboard": {
        "title": "Cyber-Sensei Application Logs",
        "description": "Real-time monitoring of application logs",
        "panels": [
            {
                "title": "Log Level Distribution",
                "type": "pie",
                "visualization": {
                    "field": "level",
                    "aggregation": "count"
                }
            },
            {
                "title": "Error Rate Over Time",
                "type": "line",
                "visualization": {
                    "field": "level",
                    "filter": {"level": "ERROR"},
                    "aggregation": "count",
                    "time_interval": "1m"
                }
            },
            {
                "title": "API Endpoint Performance",
                "type": "table",
                "visualization": {
                    "columns": ["endpoint", "response_time", "status_code"],
                    "sort": {"response_time": "desc"}
                }
            },
            {
                "title": "User Activity",
                "type": "heatmap",
                "visualization": {
                    "field": "user_id",
                    "aggregation": "cardinality",
                    "time_interval": "1h"
                }
            },
            {
                "title": "Exception Types",
                "type": "bar",
                "visualization": {
                    "field": "exception.type",
                    "aggregation": "count"
                }
            }
        ]
    }
}


# Log retention policy
LOG_RETENTION_POLICY = {
    "policy_name": "logs-retention",
    "phases": {
        "hot": {
            "min_age": "0d",
            "actions": {
                "rollover": {
                    "max_primary_shard_size": "10gb",
                    "max_age": "1d"
                },
                "set_priority": {
                    "priority": 100
                }
            }
        },
        "warm": {
            "min_age": "3d",
            "actions": {
                "set_priority": {
                    "priority": 50
                },
                "forcemerge": {
                    "max_num_segments": 1
                }
            }
        },
        "cold": {
            "min_age": "30d",
            "actions": {
                "set_priority": {
                    "priority": 0
                }
            }
        },
        "delete": {
            "min_age": "90d",
            "actions": {
                "delete": {}
            }
        }
    }
}


def setup_elasticsearch_indices():
    """Create Elasticsearch indices and mappings."""
    try:
        es = Elasticsearch(["http://localhost:9200"])
        
        # Create index template for logs
        index_template = {
            "index_patterns": ["logs-*"],
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "index.lifecycle.name": "logs-retention",
                "index.lifecycle.rollover_alias": "logs-write"
            },
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "logger": {"type": "keyword"},
                    "message": {"type": "text"},
                    "user_id": {"type": "keyword"},
                    "endpoint": {"type": "keyword"},
                    "response_time": {"type": "long"},
                    "status_code": {"type": "integer"},
                    "exception": {
                        "properties": {
                            "type": {"type": "keyword"},
                            "message": {"type": "text"}
                        }
                    }
                }
            }
        }
        
        es.indices.put_index_template(
            name="logs-template",
            body=index_template
        )
        
        logging.info("Elasticsearch indices configured")
    
    except Exception as e:
        logging.error(f"Failed to setup Elasticsearch: {e}")
