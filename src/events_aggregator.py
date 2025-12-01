#!/usr/bin/env python3
"""
Events Aggregator - Fetches events from configured sources and stores in database

Run manually: python -m src.events_aggregator
Scheduled: Daily at 6 AM via scheduler
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from .config import Config
from .database.event_operations import EventOperations
from .sources.events.skiddle_source import SkiddleSource


def setup_logging():
    """Setup logging for events aggregation"""
    os.makedirs("logs/events", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/events/events_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(),
        ],
        force=True,
    )

    logging.info(f"Events aggregation started - logging to {log_filename}")
    return log_filename


class EventsAggregator:
    """Main events aggregation orchestrator"""

    def __init__(self):
        self.db = EventOperations()
        self.sources = []
        self.logger = logging.getLogger(__name__)

        # Initialize sources
        self._init_sources()

    def _init_sources(self):
        """Initialize configured event sources"""
        # Skiddle (primary source)
        if Config.SKIDDLE_API_KEY:
            try:
                self.sources.append(SkiddleSource())
                self.logger.info("Skiddle source initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Skiddle source: {e}")
        else:
            self.logger.warning("Skiddle API key not configured, skipping")

        # Future sources would be added here
        # if Config.SOME_OTHER_SOURCE:
        #     self.sources.append(SomeOtherSource())

    def process_event(
        self, event_data: Dict[str, Any], source_name: str, source_type: str
    ) -> bool:
        """Process a single event - create venue if needed, then create event"""
        try:
            # Get or create venue
            venue_data = event_data.get("venue", {})
            venue_data["source_name"] = source_name
            venue = self.db.get_or_create_venue(venue_data)

            # Prepare event data
            event_data["source_name"] = source_name
            event_data["source_type"] = source_type

            # Insert event
            event = self.db.insert_event(event_data, venue)

            return event is not None

        except Exception as e:
            self.logger.error(
                f"Error processing event '{event_data.get('title')}': {e}"
            )
            return False

    def run_aggregation(self) -> Dict[str, int]:
        """Run aggregation from all sources"""
        self.logger.info("Starting events aggregation run")

        stats = {
            "total_fetched": 0,
            "total_inserted": 0,
            "total_duplicates": 0,
            "total_errors": 0,
        }

        for source in self.sources:
            try:
                self.logger.info(f"Fetching from source: {source.source_name}")
                events = source.fetch_events()
                stats["total_fetched"] += len(events)

                for event_data in events:
                    success = self.process_event(
                        event_data,
                        source.source_name,
                        source.source_type,
                    )
                    if success:
                        stats["total_inserted"] += 1
                    else:
                        # Could be duplicate or error
                        stats["total_duplicates"] += 1

            except Exception as e:
                self.logger.error(f"Error fetching from {source.source_name}: {e}")
                stats["total_errors"] += 1

        # Mark past events
        past_count = self.db.mark_past_events()
        self.logger.info(f"Marked {past_count} events as past")

        self.logger.info(
            f"Aggregation complete: "
            f"{stats['total_fetched']} fetched, "
            f"{stats['total_inserted']} inserted, "
            f"{stats['total_duplicates']} duplicates/skipped"
        )

        return stats

    def generate_static_json(self, output_dir: str = "static_data") -> List[str]:
        """Generate static JSON files for Jekyll frontend"""
        os.makedirs(output_dir, exist_ok=True)
        generated_files = []

        timestamp = datetime.now().isoformat()

        # 1. Events JSON (next 60 days)
        events = self.db.get_upcoming_events(limit=500)
        events_data = {
            "generated_at": timestamp,
            "events": [e.to_summary_dict() for e in events],
            "total": len(events),
        }

        events_file = os.path.join(output_dir, "events.json")
        with open(events_file, "w") as f:
            json.dump(events_data, f, indent=2, default=str)
        generated_files.append(events_file)
        self.logger.info(f"Generated {events_file} with {len(events)} events")

        # 2. Calendar JSON (next 3 months)
        calendar_data = {"generated_at": timestamp, "calendar": {}}

        now = datetime.now()
        for month_offset in range(3):
            year = now.year + (now.month + month_offset - 1) // 12
            month = (now.month + month_offset - 1) % 12 + 1

            month_data = self.db.get_calendar_data(year, month)
            calendar_data["calendar"].update(month_data)

        calendar_file = os.path.join(output_dir, "events-calendar.json")
        with open(calendar_file, "w") as f:
            json.dump(calendar_data, f, indent=2)
        generated_files.append(calendar_file)
        self.logger.info(f"Generated {calendar_file}")

        # 3. Venues JSON
        venues = self.db.get_all_venues()
        venues_data = {
            "generated_at": timestamp,
            "venues": [v.to_dict() for v in venues],
            "total": len(venues),
        }

        venues_file = os.path.join(output_dir, "venues.json")
        with open(venues_file, "w") as f:
            json.dump(venues_data, f, indent=2, default=str)
        generated_files.append(venues_file)
        self.logger.info(f"Generated {venues_file} with {len(venues)} venues")

        # 4. Event types JSON
        event_types = self.db.get_event_types()
        types_data = {
            "generated_at": timestamp,
            "event_types": event_types,
        }

        types_file = os.path.join(output_dir, "event-types.json")
        with open(types_file, "w") as f:
            json.dump(types_data, f, indent=2)
        generated_files.append(types_file)
        self.logger.info(f"Generated {types_file}")

        return generated_files

    def close(self):
        """Clean up resources"""
        self.db.close()


def run_daily_events_job():
    """Entry point for scheduled daily job"""
    setup_logging()
    logger = logging.getLogger(__name__)

    aggregator = EventsAggregator()

    try:
        # Run aggregation
        stats = aggregator.run_aggregation()

        # Generate static files
        json_files = aggregator.generate_static_json()

        logger.info(
            f"Daily events job complete. Generated {len(json_files)} static files."
        )

        return stats

    except Exception as e:
        logger.error(f"Daily events job failed: {e}")
        raise
    finally:
        aggregator.close()


if __name__ == "__main__":
    setup_logging()

    aggregator = EventsAggregator()

    try:
        # Run aggregation
        stats = aggregator.run_aggregation()
        print(f"\nAggregation stats: {stats}")

        # Generate static JSON
        files = aggregator.generate_static_json()
        print(f"\nGenerated files: {files}")

    finally:
        aggregator.close()
