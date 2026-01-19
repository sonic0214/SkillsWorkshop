#!/usr/bin/env python3
import logging
import sys
import argparse
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import yaml

from src.collector import ArticleCollector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/collector.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_collection():
    logger.info("="*60)
    logger.info(f"Starting collection at {datetime.now()}")
    try:
        collector = ArticleCollector('config.yaml')
        new_count, stats = collector.collect_all()
        logger.info(f"Done: {new_count} new, {stats['total_articles']} total")
        logger.info("="*60)
    except Exception as e:
        logger.error(f"Collection failed: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once', action='store_true', help='Run once')
    parser.add_argument('--config', default='config.yaml')
    args = parser.parse_args()
    
    import os
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    if args.once:
        run_collection()
        return
    
    with open(args.config) as f:
        config = yaml.safe_load(f)
    
    scheduler = BlockingScheduler()
    
    if config['schedule'].get('test_mode'):
        interval = config['schedule'].get('test_interval_minutes', 5)
        scheduler.add_job(run_collection, 'interval', minutes=interval, next_run_time=datetime.now())
        logger.info(f"Scheduler: every {interval} min")
    else:
        time_str = config['schedule'].get('daily_time', '08:00')
        hour, minute = map(int, time_str.split(':'))
        scheduler.add_job(run_collection, CronTrigger(hour=hour, minute=minute), next_run_time=datetime.now())
        logger.info(f"Scheduler: daily at {time_str}")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopped")

if __name__ == '__main__':
    main()
