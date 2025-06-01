import time
import logging
from functools import wraps
from typing import Callable, Any, Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics = {
            'function_calls': {},
            'api_requests': {},
            'cache_stats': {},
            'errors': []
        }

    def record_function_call(self, 
                           func_name: str, 
                           execution_time: float, 
                           success: bool,
                           error: Optional[Exception] = None) -> None:
        """Record function call performance."""
        if func_name not in self.metrics['function_calls']:
            self.metrics['function_calls'][func_name] = {
                'count': 0,
                'total_time': 0,
                'successes': 0,
                'failures': 0,
                'avg_time': 0
            }
            
        stats = self.metrics['function_calls'][func_name]
        stats['count'] += 1
        stats['total_time'] += execution_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        
        if success:
            stats['successes'] += 1
        else:
            stats['failures'] += 1
            if error:
                self.metrics['errors'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'function': func_name,
                    'error': str(error),
                    'type': type(error).__name__
                })

    def record_api_request(self,
                          endpoint: str,
                          response_time: float,
                          status_code: int) -> None:
        """Record API request performance."""
        if endpoint not in self.metrics['api_requests']:
            self.metrics['api_requests'][endpoint] = {
                'count': 0,
                'total_time': 0,
                'status_codes': {},
                'avg_time': 0
            }
            
        stats = self.metrics['api_requests'][endpoint]
        stats['count'] += 1
        stats['total_time'] += response_time
        stats['avg_time'] = stats['total_time'] / stats['count']
        
        status_str = str(status_code)
        stats['status_codes'][status_str] = stats['status_codes'].get(status_str, 0) + 1

    def update_cache_stats(self, cache_stats: Dict) -> None:
        """Update cache statistics."""
        self.metrics['cache_stats'] = cache_stats

    def get_metrics(self) -> Dict:
        """Get all collected metrics."""
        return self.metrics

    def get_performance_summary(self) -> Dict:
        """Get a summary of performance metrics."""
        summary = {
            'total_api_requests': sum(
                stats['count']
                for stats in self.metrics['api_requests'].values()
            ),
            'avg_response_time': sum(
                stats['avg_time']
                for stats in self.metrics['api_requests'].values()
            ) / len(self.metrics['api_requests']) if self.metrics['api_requests'] else 0,
            'error_count': len(self.metrics['errors']),
            'cache_hit_ratio': self.metrics['cache_stats'].get('hit_ratio', 0)
        }
        return summary
        
    def clear_metrics(self) -> None:
        """Clear all collected metrics."""
        self.metrics = {
            'function_calls': {},
            'api_requests': {},
            'cache_stats': {},
            'errors': []
        }
        
    def get_errors(self, limit: int = 10) -> list:
        """Get the most recent errors."""
        return sorted(
            self.metrics['errors'],
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
        
    def get_slowest_functions(self, limit: int = 5) -> list:
        """Get the slowest functions."""
        functions = [
            {
                'name': name,
                'avg_time': stats['avg_time'],
                'call_count': stats['count']
            }
            for name, stats in self.metrics['function_calls'].items()
        ]
        return sorted(
            functions,
            key=lambda x: x['avg_time'],
            reverse=True
        )[:limit]
        
    def get_slowest_endpoints(self, limit: int = 5) -> list:
        """Get the slowest API endpoints."""
        endpoints = [
            {
                'endpoint': endpoint,
                'avg_time': stats['avg_time'],
                'call_count': stats['count']
            }
            for endpoint, stats in self.metrics['api_requests'].items()
        ]
        return sorted(
            endpoints,
            key=lambda x: x['avg_time'],
            reverse=True
        )[:limit]
        
    def export_metrics(self, format: str = 'dict') -> Any:
        """Export metrics in different formats."""
        if format == 'dict':
            return self.metrics
        elif format == 'json':
            import json
            return json.dumps(self.metrics, default=str)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write function calls
            writer.writerow(['Function', 'Count', 'Avg Time', 'Success', 'Failure'])
            for func, stats in self.metrics['function_calls'].items():
                writer.writerow([
                    func,
                    stats['count'],
                    stats['avg_time'],
                    stats['successes'],
                    stats['failures']
                ])
                
            # Write API requests
            writer.writerow([''])
            writer.writerow(['Endpoint', 'Count', 'Avg Time'])
            for endpoint, stats in self.metrics['api_requests'].items():
                writer.writerow([
                    endpoint,
                    stats['count'],
                    stats['avg_time']
                ])
                
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")

def measure_performance(monitor: Optional[PerformanceMonitor] = None):
    """
    Decorator to measure function performance.
    
    Args:
        monitor: Optional PerformanceMonitor instance
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            error = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                execution_time = time.time() - start_time
                if monitor:
                    monitor.record_function_call(
                        func_name=func.__name__,
                        execution_time=execution_time,
                        success=error is None,
                        error=error
                    )
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            error = None
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                execution_time = time.time() - start_time
                if monitor:
                    monitor.record_function_call(
                        func_name=func.__name__,
                        execution_time=execution_time,
                        success=error is None,
                        error=error
                    )
        
        # Use appropriate wrapper based on if the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator

# Create a singleton instance
performance_monitor = PerformanceMonitor()

# Add missing import that was causing issues
import asyncio