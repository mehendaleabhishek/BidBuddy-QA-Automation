from __future__ import annotations

from dataclasses import dataclass, replace
import itertools
import time
import uuid

# Monotonic counters guarantee uniqueness even within the same millisecond.
_RUN_COUNTER = itertools.count(1)
_PROFILE_COUNTER = itertools.count(0)

PROPERTY_TYPES = (
    "Single Family Home",
    "Townhouse",
    "Condominium",
    "Duplex",
    "Multifamily",
    "Office Building",
    "Retail Space",
    "Warehouse/Industrial",
)

# Multifamily reveals extra required sub-fields; use simpler types for submit flows.
SUBMIT_SAFE_PROPERTY_TYPES = tuple(
    property_type for property_type in PROPERTY_TYPES if property_type != "Multifamily"
)

# Real address profiles — Mapbox-friendly queries with matching city/state/ZIP.
ADDRESS_PROFILES: tuple[dict[str, str], ...] = (
    {
        "query": "1600 Amphitheatre Parkway, Mountain View, California",
        "city": "Mountain View",
        "state": "CA",
        "zip_code": "94043",
    },
    {
        "query": "3151 South Babcock Street, Melbourne, Florida",
        "city": "Melbourne",
        "state": "FL",
        "zip_code": "32901",
    },
    {
        "query": "1 Infinite Loop, Cupertino, California",
        "city": "Cupertino",
        "state": "CA",
        "zip_code": "95014",
    },
    {
        "query": "350 Fifth Avenue, New York, New York",
        "city": "New York",
        "state": "NY",
        "zip_code": "10118",
    },
    {
        "query": "233 South Wacker Drive, Chicago, Illinois",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60606",
    },
    {
        "query": "1060 West Addison Street, Chicago, Illinois",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60613",
    },
    {
        "query": "123 Main Street, Pleasanton, California",
        "city": "Pleasanton",
        "state": "CA",
        "zip_code": "94566",
    },
    {
        "query": "500 South Buena Vista Street, Burbank, California",
        "city": "Burbank",
        "state": "CA",
        "zip_code": "91521",
    },
    {
        "query": "1 World Way, Los Angeles, California",
        "city": "Los Angeles",
        "state": "CA",
        "zip_code": "90045",
    },
    {
        "query": "600 Congress Avenue, Austin, Texas",
        "city": "Austin",
        "state": "TX",
        "zip_code": "78701",
    },
)


@dataclass(frozen=True)
class PropertyData:
    name: str
    address_query: str
    property_type: str
    city: str = "Melbourne"
    state: str = "FL"
    zip_code: str = "32901"
    square_footage: str = ""
    year_built: str = ""
    notes: str = "Created by BidBuddy automation."
    document_category: str = "Other"


def _unique_token() -> str:
    return f"{next(_RUN_COUNTER)}-{time.time_ns()}-{uuid.uuid4().hex[:8]}"


def _seed_index(token: str, modulo: int) -> int:
    return int(token.replace("-", "")[:12], 16) % modulo


def _generate_unique_property(**overrides: str) -> PropertyData:
    """Build a fully unique property payload for each test invocation."""
    token = _unique_token()
    profile = ADDRESS_PROFILES[next(_PROFILE_COUNTER) % len(ADDRESS_PROFILES)]

    # Keep exact Mapbox-recognized addresses; rotate profiles for uniqueness.
    address_query = profile["query"]
    property_type = SUBMIT_SAFE_PROPERTY_TYPES[
        _seed_index(token, len(SUBMIT_SAFE_PROPERTY_TYPES))
    ]
    square_footage = str(1200 + (_seed_index(token, 88000)))
    year_built = str(1950 + (_seed_index(token[::2], 74)))

    defaults = PropertyData(
        name=f"Auto Property {token}",
        address_query=address_query,
        city=profile["city"],
        state=profile["state"],
        zip_code=profile["zip_code"],
        property_type=property_type,
        square_footage=square_footage,
        year_built=year_built,
        notes=f"Automation property {token}",
        document_category="Other",
    )

    if not overrides:
        return defaults
    return replace(defaults, **overrides)


def build_property(**overrides: str) -> PropertyData:
    """Unique property for autocomplete-based create flows."""
    return _generate_unique_property(**overrides)


def build_required_property(**overrides: str) -> PropertyData:
    """Unique property for manual field entry / validation flows."""
    return _generate_unique_property(notes="", square_footage="", year_built="", **overrides)
