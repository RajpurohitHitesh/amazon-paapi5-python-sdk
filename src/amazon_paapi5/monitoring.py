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
                success = True
                return result
            except Exception as e:
                error = e
                success = False
                raise
            finally:
                execution_time = time.time() - start_time
                if monitor:
                    monitor.record_function_call(
                        func.__name__,
                        execution_time,
                        success,
                        error
                    )
                
                logger.info(
                    f"Performance: {func.__name__}",
                    extra={
                        'function': func.__name__,
                        'execution_time': execution_time,
                        'success': success,
                        'error': str(error) if error else None
                    }
                )
        return wrapper
    return decorator

# Global monitor instance
performance_monitor = PerformanceMonitor()