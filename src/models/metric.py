from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class Metric:
    """
    Represents a system metric snapshot from Datadog.
    Tracks metrics like CPU, memory, response time, etc.
    """
    
    def __init__(self, name: str, value: float, unit: str, 
                 tags: Optional[Dict[str, str]] = None,
                 timestamp: Optional[datetime] = None):
        """
        Create a new metric.
        
        Args:
            name: Metric name (e.g., 'cpu.usage', 'memory.used')
            value: Metric value
            unit: Unit of measurement (e.g., 'percent', 'bytes', 'ms')
            tags: Optional tags (e.g., {'host': 'server-01', 'env': 'production'})
            timestamp: When this metric was collected (defaults to now)
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.value = value
        self.unit = unit
        self.tags = tags or {}
        self.timestamp = timestamp or datetime.now()
        self.source = "datadog"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary for storage."""
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'tags': self.tags,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metric':
        """Create a Metric from a dictionary."""
        metric = cls(
            name=data['name'],
            value=data['value'],
            unit=data['unit'],
            tags=data.get('tags', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data.get('timestamp'), str) else data.get('timestamp')
        )
        metric.id = data['id']
        metric.source = data.get('source', 'datadog')
        return metric
    
    def __str__(self):
        return f"Metric {self.name}: {self.value} {self.unit}"
