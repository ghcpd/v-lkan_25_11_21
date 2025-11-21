#!/usr/bin/env python3
"""
Main application for continuous metrics collection
"""

import argparse
import json
import logging
import signal
import sys
import time
from pathlib import Path

from collector import MetricsCollector
from storage import MetricsStorage
from reporter import MetricsReporter


class MetricsApp:
    """Main application for metrics collection"""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize application with configuration"""
        self.running = False
        self.config = self._load_config(config_file)
        self._setup_logging()
        
        # Initialize components
        self.collector = MetricsCollector()
        self.storage = MetricsStorage(
            output_dir=self.config['output_directory'],
            metrics_file=self.config['metrics_file'],
            max_file_size_mb=self.config['max_file_size_mb'],
            rotate_files=self.config['rotate_files']
        )
        self.reporter = MetricsReporter()
        
        self.logger.info("Metrics application initialized")
    
    def _load_config(self, config_file: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('metrics_app.log')
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def collect_once(self):
        """Collect metrics once and store"""
        try:
            metrics = self.collector.collect_all_metrics()
            success = self.storage.write_metric(metrics)
            
            if success:
                self.logger.debug(f"Metric collected at timestamp {metrics['timestamp']}")
            else:
                self.logger.error("Failed to write metric")
            
            return success
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return False
    
    def run_continuous(self, duration: int = None):
        """
        Run continuous metrics collection
        
        Args:
            duration: Optional duration in seconds (None for infinite)
        """
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info("Starting continuous metrics collection")
        self.logger.info(f"Collection interval: {self.config['collection_interval']} seconds")
        
        start_time = time.time()
        collection_count = 0
        
        try:
            while self.running:
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    self.logger.info(f"Duration limit of {duration}s reached")
                    break
                
                # Collect metrics
                if self.collect_once():
                    collection_count += 1
                
                # Wait for next collection
                time.sleep(self.config['collection_interval'])
        
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        
        finally:
            self.logger.info(f"Collection stopped. Total metrics collected: {collection_count}")
            self._print_summary()
    
    def generate_report(self, output_file: str = None):
        """Generate summary report from collected metrics"""
        if output_file is None:
            output_file = str(Path(self.config['output_directory']) / self.config['summary_file'])
        
        metrics_file = str(Path(self.config['output_directory']) / self.config['metrics_file'])
        
        self.logger.info(f"Generating report from {metrics_file}")
        
        success = self.reporter.generate_and_save_report(metrics_file, output_file)
        
        if success:
            self.logger.info(f"Report generated: {output_file}")
        else:
            self.logger.error("Failed to generate report")
        
        return success
    
    def _print_summary(self):
        """Print summary of current metrics file"""
        info = self.storage.get_file_info()
        
        print("\n" + "="*60)
        print("METRICS COLLECTION SUMMARY")
        print("="*60)
        print(f"Metrics file: {info['path']}")
        print(f"File size: {info['size_mb']:.2f} MB ({info['size_bytes']:,} bytes)")
        print(f"Total records: {info['record_count']}")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="System Metrics Collection Framework"
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    
    parser.add_argument(
        '--mode',
        choices=['collect', 'report', 'once'],
        default='collect',
        help='Operation mode: collect (continuous), report (generate report), once (single collection)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        help='Collection duration in seconds (for continuous mode)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for report mode'
    )
    
    args = parser.parse_args()
    
    # Initialize application
    app = MetricsApp(config_file=args.config)
    
    # Execute based on mode
    if args.mode == 'once':
        app.collect_once()
        app._print_summary()
    
    elif args.mode == 'collect':
        app.run_continuous(duration=args.duration)
    
    elif args.mode == 'report':
        app.generate_report(output_file=args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
