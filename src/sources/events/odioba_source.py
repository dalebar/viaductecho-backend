"""
Odioba DJ events source - scrapes https://odioba.com/djs

Uses Playwright for JavaScript rendering as the site is client-side rendered.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from playwright.sync_api import sync_playwright

from .base_event_source import BaseEventSource

try:
    from ...config import Config
except ImportError:
    from config import Config


class OdiobaSource(BaseEventSource):
    """Fetch DJ events from Odioba venue website"""

    def __init__(self):
        super().__init__(source_name="odioba", source_type="scrape")
        self.base_url = "https://odioba.com/djs"

        # Hardcoded venue info (single venue source)
        self.venue_data = {
            "name": "Odioba",
            "address_line1": "26 Lower Hillgate",
            "town": "Stockport",
            "postcode": "SK1 1JE",
            "latitude": 53.4088,
            "longitude": -2.1584,
            "source_id": "odioba-venue",
            "source_name": "odioba",
        }

        # Month map for parsing
        self.month_map = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }

    def _parse_time_range(self, time_text: str) -> tuple[Optional[str], Optional[str]]:
        """Parse time range like '19:00-01:00' or '14:00-20:00'"""
        try:
            match = re.search(r"(\d{1,2}:\d{2})-(\d{1,2}:\d{2})", time_text)
            if match:
                return match.group(1), match.group(2)
            return None, None
        except Exception:
            return None, None

    def _parse_events_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse events from the page text content"""
        events = []
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Day abbreviations to look for
        day_abbrevs = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        i = 0
        while i < len(lines):
            # Look for day abbreviation starting an event block
            if lines[i] in day_abbrevs:
                # Next should be month
                if i + 1 >= len(lines):
                    i += 1
                    continue
                month_str = lines[i + 1].lower()
                if month_str not in self.month_map:
                    i += 1
                    continue

                # Next should be day with ordinal (e.g., "31st", "4th")
                if i + 2 >= len(lines):
                    i += 1
                    continue
                day_match = re.match(r"(\d{1,2})(?:st|nd|rd|th)", lines[i + 2])
                if not day_match:
                    i += 1
                    continue

                day = int(day_match.group(1))
                month = self.month_map[month_str]

                # Determine year
                now = datetime.now()
                year = now.year
                try:
                    event_date = datetime(year, month, day)
                    if event_date.date() < now.date():
                        event_date = datetime(year + 1, month, day)
                except ValueError:
                    i += 1
                    continue

                # Next line should be the event title
                if i + 3 >= len(lines):
                    i += 1
                    continue
                title = lines[i + 3]

                # Skip if title looks like it's not an event title
                if title in day_abbrevs or title.lower() in self.month_map:
                    i += 1
                    continue

                # Gather description and time from following lines
                description_parts = []
                start_time = "21:00"  # Default
                end_time = None

                j = i + 4
                while j < len(lines) and lines[j] not in day_abbrevs:
                    line = lines[j]

                    # Check for time range
                    time_match = re.search(r"(\d{1,2}:\d{2})-(\d{1,2}:\d{2})", line)
                    if time_match:
                        start_time = time_match.group(1)
                        end_time = time_match.group(2)
                    # Skip location line (contains Ōdiobā address)
                    elif "diob" in line.lower() or "hillgate" in line.lower():
                        pass
                    # Skip "Event Details" or "More Events" lines
                    elif line in ["Event Details", "More Events", "..."]:
                        pass
                    # Add to description
                    elif not line.startswith("http") and len(line) > 3:
                        description_parts.append(line)

                    j += 1

                # Set the time on the date
                hour, minute = map(int, start_time.split(":"))
                event_date = event_date.replace(hour=hour, minute=minute)

                # Calculate end datetime if available
                end_datetime = None
                if end_time:
                    end_hour, end_minute = map(int, end_time.split(":"))
                    end_datetime = event_date.replace(hour=end_hour, minute=end_minute)
                    # If end time is earlier than start, it's next day
                    if end_datetime <= event_date:
                        from datetime import timedelta

                        end_datetime = end_datetime + timedelta(days=1)

                # Build description
                description = (
                    " ".join(description_parts)
                    if description_parts
                    else f"{title} at Odioba"
                )

                # Create unique source_id
                title_slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:30].strip("-")
                source_id = f"odioba-{event_date.strftime('%Y%m%d')}-{title_slug}"

                event_data = {
                    "title": title,
                    "description": description,
                    "short_description": title[:100],
                    "start_datetime": event_date,
                    "end_datetime": end_datetime,
                    "doors_time": None,
                    "event_type": "music",
                    "image_url": Config.ODIOBA_DEFAULT_IMAGE,
                    "ticket_url": self.base_url,
                    "price_min": None,
                    "price_max": None,
                    "is_free": "free" in description.lower() or "free" in title.lower(),
                    "source_id": source_id,
                    "source_url": self.base_url,
                    "venue": self.venue_data.copy(),
                }

                # Avoid duplicates
                if not any(e["source_id"] == source_id for e in events):
                    events.append(event_data)
                    self.logger.debug(
                        f"Found event: {title} on {event_date.strftime('%Y-%m-%d %H:%M')}"
                    )

                # Move to next potential event
                i = j
            else:
                i += 1

        return events

    def fetch_events(self) -> List[Dict[str, Any]]:
        """Fetch DJ events from Odioba website using Playwright"""
        events = []

        try:
            self.logger.info("Fetching Odioba DJ events with Playwright...")

            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Navigate to the DJs page
                page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)

                # Wait for JS content to render
                page.wait_for_timeout(5000)

                # Get page text content
                text = page.inner_text("body")

                browser.close()

            # Parse events from text
            events = self._parse_events_from_text(text)

            self.logger.info(f"Odioba: {len(events)} events found")
            return events

        except Exception as e:
            self.logger.error(f"Odioba fetch error: {e}")
            return []
