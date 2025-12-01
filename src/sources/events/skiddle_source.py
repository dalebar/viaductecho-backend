"""
Skiddle API integration for event sourcing

API Docs: https://github.com/Skiddle/web-api
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

try:
    from ...config import Config
except ImportError:
    from config import Config

from .base_event_source import BaseEventSource


class SkiddleSource(BaseEventSource):
    """Fetch events from Skiddle API"""

    BASE_URL = "https://www.skiddle.com/api/v1"

    def __init__(self):
        super().__init__(source_name="skiddle", source_type="api")
        self.api_key = Config.SKIDDLE_API_KEY

        if not self.api_key:
            raise ValueError("SKIDDLE_API_KEY not configured")

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict]:
        """Make API request to Skiddle"""
        if params is None:
            params = {}

        params["api_key"] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"

        try:
            timeout = Config.HTTP_TIMEOUT if Config.HTTP_TIMEOUT else 30
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Skiddle API request failed: {e}")
            return None

    def _map_event_type(self, skiddle_code: str) -> str:
        """Map Skiddle event code to our event type"""
        return Config.SKIDDLE_EVENT_TYPE_MAP.get(skiddle_code, "other")

    def _parse_event(self, raw_event: Dict) -> Optional[Dict[str, Any]]:
        """Parse raw Skiddle event data into our format"""
        try:
            # Parse date/time
            date_str = raw_event.get("date", "")
            time_str = raw_event.get("openingtimes", {}).get("doorsopen", "19:00")

            if not date_str:
                return None

            # Combine date and time
            try:
                start_datetime = datetime.strptime(
                    f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
                )
            except ValueError:
                start_datetime = datetime.strptime(date_str, "%Y-%m-%d")

            # Parse venue
            venue_data = raw_event.get("venue", {})
            venue = {
                "name": venue_data.get("name", "Unknown Venue"),
                "address_line1": venue_data.get("address", ""),
                "town": venue_data.get("town", ""),
                "postcode": venue_data.get("postcode", ""),
                "latitude": venue_data.get("latitude"),
                "longitude": venue_data.get("longitude"),
                "source_id": str(venue_data.get("id", "")),
                "source_name": "skiddle",
            }

            # Parse prices
            entry_price = raw_event.get("entryprice", "")
            is_free = entry_price.lower() == "free" if entry_price else False

            price_min = None
            price_max = None

            if not is_free and entry_price:
                # Try to extract numeric price
                try:
                    # Remove currency symbols and parse
                    price_str = entry_price.replace("£", "").replace(",", "").strip()
                    if "-" in price_str:
                        parts = price_str.split("-")
                        price_min = float(parts[0].strip())
                        price_max = float(parts[1].strip())
                    else:
                        price_min = float(price_str)
                        price_max = price_min
                except (ValueError, IndexError):
                    pass

            # Get description
            description = raw_event.get("description", "")
            short_description = description[:500] if description else None

            # Get image
            image_url = raw_event.get("largeimageurl") or raw_event.get("imageurl")

            return {
                "title": raw_event.get("eventname", "Untitled Event"),
                "description": description,
                "short_description": short_description,
                "start_datetime": start_datetime,
                "end_datetime": None,  # Skiddle doesn't provide end times reliably
                "doors_time": None,
                "event_type": self._map_event_type(raw_event.get("eventcode", "")),
                "image_url": image_url,
                "ticket_url": raw_event.get("link", ""),
                "price_min": price_min,
                "price_max": price_max,
                "is_free": is_free,
                "source_id": str(raw_event.get("id", "")),
                "source_url": raw_event.get("link", ""),
                "venue": venue,
            }

        except Exception as e:
            self.logger.error(f"Error parsing Skiddle event: {e}")
            return None

    def fetch_events(self) -> List[Dict[str, Any]]:
        """Fetch events from Skiddle API"""
        all_events = []

        # Calculate date range
        min_date = datetime.now().strftime("%Y-%m-%d")
        max_date = (
            datetime.now() + timedelta(days=Config.EVENTS_FETCH_DAYS_AHEAD)
        ).strftime("%Y-%m-%d")

        # Fetch with pagination
        offset = 0
        limit = 100  # Skiddle max

        while True:
            params = {
                "latitude": Config.EVENTS_LATITUDE,
                "longitude": Config.EVENTS_LONGITUDE,
                "radius": Config.EVENTS_RADIUS_MILES,
                "minDate": min_date,
                "maxDate": max_date,
                "limit": limit,
                "offset": offset,
                "description": 1,  # Include full descriptions
            }

            self.logger.info(f"Fetching Skiddle events (offset={offset})...")
            response = self._make_request("events/search/", params)

            if not response:
                break

            results = response.get("results", [])

            if not results:
                break

            for raw_event in results:
                parsed = self._parse_event(raw_event)
                if parsed:
                    all_events.append(parsed)

            self.logger.info(f"Fetched {len(results)} events from Skiddle")

            # Check if more pages
            if len(results) < limit:
                break

            offset += limit

            # Safety limit
            if offset >= 1000:
                self.logger.warning("Reached safety limit of 1000 events")
                break

        # Filter by postcode
        filtered_events = self.filter_by_postcode(
            all_events, Config.VALID_POSTCODE_PREFIXES
        )

        # Also include events matching keywords even if outside SK postcode
        keyword_events = self.filter_by_keywords(
            [e for e in all_events if e not in filtered_events], Config.KEYWORDS
        )

        final_events = filtered_events + keyword_events

        self.logger.info(
            f"Skiddle: {len(all_events)} total, {len(final_events)} after filtering"
        )

        return final_events
