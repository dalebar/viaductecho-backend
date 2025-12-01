"""
Base class for event sources
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseEventSource(ABC):
    """Abstract base class for event data sources"""

    def __init__(self, source_name: str, source_type: str):
        self.source_name = source_name
        self.source_type = source_type  # 'api', 'scrape', 'manual'
        self.logger = logging.getLogger(f"{__name__}.{source_name}")

    @abstractmethod
    def fetch_events(self) -> List[Dict[str, Any]]:
        """
        Fetch events from the source.

        Returns list of event dictionaries with structure:
        {
            "title": str,
            "description": str,
            "short_description": str,
            "start_datetime": datetime,
            "end_datetime": datetime (optional),
            "doors_time": time (optional),
            "event_type": str,
            "image_url": str (optional),
            "ticket_url": str (optional),
            "price_min": float (optional),
            "price_max": float (optional),
            "is_free": bool,
            "source_id": str,
            "source_url": str,
            "venue": {
                "name": str,
                "address_line1": str,
                "town": str,
                "postcode": str,
                "latitude": float,
                "longitude": float,
                "source_id": str,
            }
        }
        """
        pass

    def filter_by_postcode(
        self, events: List[Dict], valid_prefixes: List[str]
    ) -> List[Dict]:
        """Filter events to only include valid postcodes"""
        filtered = []
        for event in events:
            venue = event.get("venue", {})
            postcode = venue.get("postcode", "")
            if postcode:
                prefix = postcode.split()[0] if " " in postcode else postcode[:2]
                if any(prefix.upper().startswith(p) for p in valid_prefixes):
                    filtered.append(event)
                    continue

            # Also include if venue name/town matches keywords
            town = venue.get("town", "").lower()
            name = venue.get("name", "").lower()
            if "stockport" in town or "stockport" in name:
                filtered.append(event)

        return filtered

    def filter_by_keywords(self, events: List[Dict], keywords: List[str]) -> List[Dict]:
        """Filter events by keyword matching in title/description"""
        filtered = []
        keywords_lower = [k.lower() for k in keywords]

        for event in events:
            title = event.get("title", "").lower()
            description = event.get("description", "").lower()
            venue_name = event.get("venue", {}).get("name", "").lower()
            venue_town = event.get("venue", {}).get("town", "").lower()

            # Check if any keyword matches
            text_to_search = f"{title} {description} {venue_name} {venue_town}"
            if any(kw in text_to_search for kw in keywords_lower):
                filtered.append(event)

        return filtered
