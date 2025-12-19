"""MLflow experiment tracking for agent evaluation and performance monitoring."""

import os
import statistics
from contextlib import contextmanager
from typing import Any, Optional

from agentic_ai.config.settings import get_settings
from agentic_ai.monitoring.logging import get_logger

logger = get_logger(__name__)

# Try to import MLflow, make it optional
try:
    import mlflow
    from mlflow import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    mlflow = None
    MlflowClient = None


class MLflowTracker:
    """MLflow experiment tracker for agent performance and evaluation."""

    def __init__(self):
        """Initialize MLflow tracker."""
        self.settings = get_settings()
        self._enabled = self.settings.mlflow_enabled and MLFLOW_AVAILABLE
        self._active_run: Optional[Any] = None
        self._latency_samples: list[float] = []

        if not MLFLOW_AVAILABLE:
            logger.warning("MLflow not installed. Install with: pip install mlflow")
            return

        if not self._enabled:
            logger.info("MLflow tracking disabled")
            return

        # Set tracking URI (defaults to local ./mlruns)
        if self.settings.mlflow_tracking_uri:
            mlflow.set_tracking_uri(self.settings.mlflow_tracking_uri)
        else:
            # Use local directory
            mlruns_dir = os.path.join(os.getcwd(), "mlruns")
            os.makedirs(mlruns_dir, exist_ok=True)
            mlflow.set_tracking_uri(f"file://{mlruns_dir}")

        # Set or create experiment
        try:
            mlflow.set_experiment(self.settings.mlflow_experiment_name)
        except Exception as e:
            logger.warning(f"Failed to set MLflow experiment: {e}")

        logger.info(f"MLflow tracker initialized (experiment: {self.settings.mlflow_experiment_name})")

    @contextmanager
    def start_run(self, run_name: Optional[str] = None, tags: Optional[dict[str, str]] = None):
        """Start an MLflow run as a context manager.

        Args:
            run_name: Optional run name
            tags: Optional tags to attach to the run

        Yields:
            MLflow run object
        """
        if not self._enabled:
            yield None
            return

        try:
            with mlflow.start_run(run_name=run_name, tags=tags or {}):
                self._active_run = mlflow.active_run()
                self._latency_samples = []  # Reset latency samples for this run
                yield self._active_run
        except Exception as e:
            logger.error(f"MLflow run error: {e}", exc_info=True)
            yield None
        finally:
            self._active_run = None
            self._latency_samples = []

    def log_params(self, params: dict[str, Any]) -> None:
        """Log hyperparameters to MLflow.

        Args:
            params: Dictionary of parameter names and values
        """
        if not self._enabled or not mlflow.active_run():
            return

        try:
            mlflow.log_params(params)
            logger.debug(f"Logged parameters: {list(params.keys())}")
        except Exception as e:
            logger.warning(f"Failed to log parameters to MLflow: {e}")

    def log_metrics(self, metrics: dict[str, float], step: Optional[int] = None) -> None:
        """Log metrics to MLflow.

        Args:
            metrics: Dictionary of metric names and values
            step: Optional step number for time-series metrics
        """
        if not self._enabled or not mlflow.active_run():
            return

        try:
            mlflow.log_metrics(metrics, step=step)
            logger.debug(f"Logged metrics: {list(metrics.keys())}")
        except Exception as e:
            logger.warning(f"Failed to log metrics to MLflow: {e}")

    def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None:
        """Log a single metric to MLflow.

        Args:
            key: Metric name
            value: Metric value
            step: Optional step number
        """
        if not self._enabled or not mlflow.active_run():
            return

        try:
            mlflow.log_metric(key, value, step=step)
        except Exception as e:
            logger.warning(f"Failed to log metric {key} to MLflow: {e}")

    def log_latency(self, latency_seconds: float) -> None:
        """Record a latency sample for percentile calculations.

        Args:
            latency_seconds: Latency in seconds
        """
        if not self._enabled:
            return

        self._latency_samples.append(latency_seconds)

    def log_latency_percentiles(self) -> None:
        """Calculate and log latency percentiles (P50, P95, P99).

        This should be called at the end of a run after collecting latency samples.
        """
        if not self._enabled or not self._latency_samples:
            return

        try:
            sorted_latencies = sorted(self._latency_samples)
            n = len(sorted_latencies)

            percentiles = {
                "latency_p50_ms": sorted_latencies[int(n * 0.50)] * 1000,
                "latency_p95_ms": sorted_latencies[int(n * 0.95)] * 1000,
                "latency_p99_ms": sorted_latencies[int(n * 0.99)] * 1000,
                "latency_mean_ms": statistics.mean(sorted_latencies) * 1000,
                "latency_min_ms": min(sorted_latencies) * 1000,
                "latency_max_ms": max(sorted_latencies) * 1000,
            }

            self.log_metrics(percentiles)
            logger.info(f"Logged latency percentiles: P50={percentiles['latency_p50_ms']:.2f}ms, "
                       f"P95={percentiles['latency_p95_ms']:.2f}ms, "
                       f"P99={percentiles['latency_p99_ms']:.2f}ms")
        except Exception as e:
            logger.warning(f"Failed to log latency percentiles: {e}")

    def log_tags(self, tags: dict[str, str]) -> None:
        """Log tags to the current run.

        Args:
            tags: Dictionary of tag names and values
        """
        if not self._enabled or not mlflow.active_run():
            return

        try:
            mlflow.set_tags(tags)
            logger.debug(f"Logged tags: {list(tags.keys())}")
        except Exception as e:
            logger.warning(f"Failed to log tags to MLflow: {e}")

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """Log an artifact (file) to MLflow.

        Args:
            local_path: Path to the local file to log
            artifact_path: Optional path within the artifact directory
        """
        if not self._enabled or not mlflow.active_run():
            return

        try:
            mlflow.log_artifact(local_path, artifact_path)
            logger.debug(f"Logged artifact: {local_path}")
        except Exception as e:
            logger.warning(f"Failed to log artifact to MLflow: {e}")

    @property
    def is_enabled(self) -> bool:
        """Check if MLflow tracking is enabled."""
        return self._enabled

    @property
    def active_run(self) -> Optional[Any]:
        """Get the currently active MLflow run."""
        return self._active_run if self._enabled else None


# Global tracker instance
_tracker: Optional[MLflowTracker] = None


def get_mlflow_tracker() -> MLflowTracker:
    """Get the global MLflow tracker instance.

    Returns:
        MLflowTracker instance
    """
    global _tracker
    if _tracker is None:
        _tracker = MLflowTracker()
    return _tracker

