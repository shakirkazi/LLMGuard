"""Default PII entity configurations for the PIIFilter."""

# Entities enabled by default when no explicit list is provided
DEFAULT_ENTITIES = [
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "US_SSN",
    "CREDIT_CARD",
    "IP_ADDRESS",
    "PERSON",
    "LOCATION",
    "DATE_TIME",
]

# Friendly aliases that map to Presidio entity names
ENTITY_ALIASES = {
    "EMAIL": "EMAIL_ADDRESS",
    "PHONE": "PHONE_NUMBER",
    "SSN": "US_SSN",
    "CREDIT_CARD": "CREDIT_CARD",
    "IP_ADDRESS": "IP_ADDRESS",
    "PERSON": "PERSON",
    "LOCATION": "LOCATION",
    "DATE_TIME": "DATE_TIME",
}


def resolve_entity(name: str) -> str:
    """Resolve a friendly entity alias to the Presidio entity name."""
    upper = name.upper()
    return ENTITY_ALIASES.get(upper, upper)
