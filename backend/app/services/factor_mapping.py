"""
Purpose: Deterministically convert the raw category attributes received
from the external data-collection system (nature of data, identifiability,
localization capability, collection frequency, access scope, sharing
scope) into 0-4 factor ratings, following the exact category order
defined in the conference paper's scoring table (Section 3.3.3).

Sensitivity is the one factor NOT received from the external system —
it is deduced by this application from Data type and Identifiability,
on the reasoning that how much a data stream reveals about someone's
private life follows directly from what kind of data it is and how
easily it can be tied to a specific person. This is a documented
methodology choice, not an external input.
"""

# Each list is ordered exactly as the paper's table: index 0 -> Score 0,
# index 4 -> Score 4. The external system is expected to send one of
# these exact category keys per instance.
DATA_NATURE_SCALE = [
    "environmental",           # Score 0 — temperature, humidity
    "non_personal_usage",      # Score 1 — energy consumption patterns
    "behavioural",             # Score 2 — presence, movement
    "behavioural_contextual",  # Score 3 — routine inference
    "identity_biometric",      # Score 4 — face, fingerprint
]

IDENTIFIABILITY_SCALE = [
    "cannot_link",              # Score 0
    "significant_effort",       # Score 1 — linkable only with major extra effort/external data
    "additional_information",   # Score 2 — linkable with additional information
    "minimal_information",      # Score 3 — linkable with minimal additional information
    "direct",                   # Score 4 — directly and reliably identifies
]

LOCATION_SCOPE_SCALE = [
    "none",                     # Score 0 — no spatial information
    "building_level",           # Score 1
    "room_zone",                # Score 2
    "room_zone_over_time",      # Score 3
    "precise_continuous",       # Score 4
]

COLLECTION_FREQUENCY_SCALE = [
    "occasional",       # Score 0 — rare, event-triggered
    "weekly_several",   # Score 1 — several times per week
    "periodic",         # Score 2 — a few times per day
    "frequent",         # Score 3 — hourly / near-continuous
    "continuous",        # Score 4 — real-time
]

ACCESS_SCOPE_SCALE = [
    "key_personnel",         # Score 0 — 1-2 key personnel
    "small_team",             # Score 1 — small, clearly defined team
    "defined_group",          # Score 2 — e.g. security + HR
    "multiple_departments",   # Score 3 — multiple departments, no strict limits
    "broadly_accessible",     # Score 4 — weakly restricted
]

SHARING_SCOPE_SCALE = [
    "not_shared",                  # Score 0 — not shared beyond the collecting system
    "same_subsystem",              # Score 1
    "internal_services",           # Score 2 — internal building services
    "external_partner_contract",   # Score 3 — external partner under contractual control
    "external_third_party",        # Score 4
]


class InvalidAttributeError(Exception):
    """Raised when a raw category value isn't one of the defined scale keys."""
    pass


def _score_from_scale(value: str, scale: list, field_name: str) -> int:
    if value not in scale:
        raise InvalidAttributeError(
            f"'{value}' is not a valid value for {field_name}. Expected one of: {scale}"
        )
    return scale.index(value)


def compute_factor_ratings(instance) -> dict:
    """Returns a dict of {factor_name: rating} for all 7 factors, derived
    from this instance's raw category attributes."""
    data_type = _score_from_scale(instance.data_nature, DATA_NATURE_SCALE, "data_nature")
    identifiability = _score_from_scale(instance.identifiability_level, IDENTIFIABILITY_SCALE, "identifiability_level")
    location_tracking = _score_from_scale(instance.location_scope, LOCATION_SCOPE_SCALE, "location_scope")
    frequency = _score_from_scale(instance.collection_frequency, COLLECTION_FREQUENCY_SCALE, "collection_frequency")
    access_control = _score_from_scale(instance.access_scope, ACCESS_SCOPE_SCALE, "access_scope")
    data_sharing = _score_from_scale(instance.sharing_scope, SHARING_SCOPE_SCALE, "sharing_scope")

    # Sensitivity deduction rule: the average of Data type and
    # Identifiability, rounded to the nearest integer. Rationale: a data
    # stream reveals more about someone's private life when it is both
    # (a) inherently personal/behavioural in nature and (b) easily tied
    # to a specific individual — e.g. identity/biometric data that also
    # directly identifies someone (4, 4) should read as highly sensitive
    # (4), while environmental data that cannot be linked to anyone
    # (0, 0) should read as not sensitive (0).
    sensitivity = round((data_type + identifiability) / 2)

    return {
        "Data type": data_type,
        "Sensitivity": sensitivity,
        "Identifiability": identifiability,
        "Location tracking": location_tracking,
        "Frequency of collection": frequency,
        "Access control": access_control,
        "Data sharing": data_sharing,
    }