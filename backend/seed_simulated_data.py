import random
from datetime import datetime, timedelta, timezone
from app import create_app, db
from app.models import Device, CollectionInstance, InstanceFactorScore, RiskFactor, DeviceDataSample
from app.services.factor_mapping import compute_factor_ratings, InvalidAttributeError

"""
Purpose: Generate simulated CollectionInstance records (with their raw
category attributes) and DeviceDataSample records for every device that
doesn't already have instances, based on what its DeviceType actually
collects (primary_data_collected). This script plays the role of the
external data-collection system described in the project's design: in
a real deployment, another application would report these raw
attributes (nature of data, identifiability, location scope, collection
frequency, access scope, sharing scope) for each collection instance;
here, they are assigned directly per data category, grounded in the
paper's Figure 3 (device/data mapping) and Section 3.3.3 (scoring
table categories).

Factor ratings are NOT assigned directly or randomly — they are always
computed deterministically from the raw attributes via
app.services.factor_mapping.compute_factor_ratings(), exactly as the
real ingestion route (/api/instances/ingest) would do. Sensitivity in
particular is never set here: it is deduced from Data type and
Identifiability by that same shared function, so the seed data and any
future real ingestion follow the exact same rule.

There is no active/inactive concept: every instance counts toward its
device's score, and the number/spacing of simulated samples is derived
from the instance's own collection_frequency category.

Everything below is read-only in the interface (Section 3.3.6).

How to run it:
    docker compose exec backend python seed_simulated_data.py
"""

# Raw attribute profile per category of data point, using the exact
# category keys defined in app.services.factor_mapping (which mirror
# the paper's Section 3.3.3 table). Sensitivity is intentionally absent
# here — it is always deduced, never assigned directly.
#
# Justification per device/data category is grounded in the paper's
# examples (Figure 3 for device mapping, Section 3.3.3 for what each
# category label means):
RAW_ATTRIBUTE_PROFILES = {
    # HVAC — environmental data, no location beyond the room it's in,
    # polled frequently for control purposes, small facilities team,
    # stays within the BMS.
    "temperature": {
        "data_nature": "environmental", "identifiability_level": "cannot_link",
        "location_scope": "room_zone", "collection_frequency": "frequent",
        "access_scope": "small_team", "sharing_scope": "not_shared",
    },
    "humidity": {
        "data_nature": "environmental", "identifiability_level": "cannot_link",
        "location_scope": "room_zone", "collection_frequency": "frequent",
        "access_scope": "small_team", "sharing_scope": "not_shared",
    },

    # Presence/occupancy — behavioural data, cannot identify a specific
    # person (PIR-type sensors don't distinguish individuals), room/zone
    # level, near-continuous triggering, small team, internal only.
    "inferred presence": {
        "data_nature": "behavioural", "identifiability_level": "cannot_link",
        "location_scope": "room_zone", "collection_frequency": "frequent",
        "access_scope": "small_team", "sharing_scope": "not_shared",
    },
    "presence": {
        "data_nature": "behavioural", "identifiability_level": "cannot_link",
        "location_scope": "room_zone", "collection_frequency": "frequent",
        "access_scope": "small_team", "sharing_scope": "not_shared",
    },
    "zone occupancy": {
        "data_nature": "behavioural", "identifiability_level": "cannot_link",
        "location_scope": "room_zone", "collection_frequency": "frequent",
        "access_scope": "small_team", "sharing_scope": "not_shared",
    },
    "vehicle presence": {
        "data_nature": "behavioural", "identifiability_level": "cannot_link",
        "location_scope": "room_zone", "collection_frequency": "periodic",
        "access_scope": "small_team", "sharing_scope": "not_shared",
    },

    # Access/identity events — behavioural data with contextual detail
    # (repeated badge scans reveal a routine), directly identifying,
    # room/zone-level (which door), periodic (a few scans a day),
    # accessible to a defined security+HR group, shared with internal
    # building services (e.g. HR records).
    "identity": {
        "data_nature": "behavioural_contextual", "identifiability_level": "direct",
        "location_scope": "room_zone", "collection_frequency": "periodic",
        "access_scope": "defined_group", "sharing_scope": "internal_services",
    },
    "access timestamps": {
        "data_nature": "behavioural", "identifiability_level": "additional_information",
        "location_scope": "room_zone", "collection_frequency": "periodic",
        "access_scope": "defined_group", "sharing_scope": "same_subsystem",
    },

    # Video/image — identity/biometric data by definition, directly
    # identifies, tracks a zone continuously over time, real-time
    # collection, restricted to a defined security team, but commonly
    # relayed to an external monitoring/storage provider under contract.
    "video/image": {
        "data_nature": "identity_biometric", "identifiability_level": "direct",
        "location_scope": "room_zone_over_time", "collection_frequency": "continuous",
        "access_scope": "defined_group", "sharing_scope": "external_partner_contract",
    },

    # LPR camera — identity/biometric-equivalent (a plate reliably
    # identifies a vehicle/owner), event-triggered rather than
    # continuous, room/zone-level (entry/exit point), sometimes shared
    # with an external authority/operator under contract.
    "plate identifier": {
        "data_nature": "identity_biometric", "identifiability_level": "direct",
        "location_scope": "room_zone", "collection_frequency": "periodic",
        "access_scope": "defined_group", "sharing_scope": "external_partner_contract",
    },

    # Fire & life safety — environmental data, cannot identify anyone,
    # zone-level, strictly rare/event-triggered (a fire/gas event is
    # rare), restricted to key safety personnel, stays internal.
    "environmental data": {
        "data_nature": "environmental", "identifiability_level": "cannot_link",
        "location_scope": "room_zone", "collection_frequency": "occasional",
        "access_scope": "key_personnel", "sharing_scope": "same_subsystem",
    },
    "event location": {
        "data_nature": "environmental", "identifiability_level": "cannot_link",
        "location_scope": "room_zone", "collection_frequency": "occasional",
        "access_scope": "key_personnel", "sharing_scope": "same_subsystem",
    },

    # Electrical — non-personal usage data (load curves), cannot be
    # linked to an individual without significant extra effort,
    # building-level only, near-continuous smart-meter reporting,
    # small facilities team, typically shared with the utility provider
    # under contract.
    "electricity consumption": {
        "data_nature": "non_personal_usage", "identifiability_level": "significant_effort",
        "location_scope": "building_level", "collection_frequency": "continuous",
        "access_scope": "small_team", "sharing_scope": "external_partner_contract",
    },

    # Water — non-personal usage data, cannot link, building-level,
    # collected less often than electricity, internal only.
    "water consumption": {
        "data_nature": "non_personal_usage", "identifiability_level": "cannot_link",
        "location_scope": "building_level", "collection_frequency": "weekly_several",
        "access_scope": "small_team", "sharing_scope": "not_shared",
    },

    # Cross-subsystem occupancy — behavioural data, cannot identify a
    # specific individual (aggregate counting/PIR), zone-level tracked
    # over time as a person moves through the building, frequent
    # updates, small team, internal only.
    "indoor localisation": {
        "data_nature": "behavioural", "identifiability_level": "cannot_link",
        "location_scope": "room_zone_over_time", "collection_frequency": "frequent",
        "access_scope": "small_team", "sharing_scope": "not_shared",
    },
}

DEFAULT_ATTRIBUTES = {
    "data_nature": "non_personal_usage", "identifiability_level": "significant_effort",
    "location_scope": "building_level", "collection_frequency": "periodic",
    "access_scope": "small_team", "sharing_scope": "not_shared",
}

# Number of simulated samples and their spacing, derived from the
# collection_frequency category actually assigned to an instance — this
# is not an instant-T snapshot: a "continuous" instance produces many
# closely-spaced samples over a short recent window, while an
# "occasional" instance produces only 1-2 samples spread over a month.
FREQUENCY_TO_SAMPLING = {
    "occasional":     (30, None, (1, 2)),          # rare event-triggered: scattered over a month
    "weekly_several": (14, 60 * 24 * 2, (4, 6)),     # every 2-3 days over 2 weeks
    "periodic":       (3, 60 * 5, (6, 10)),          # every ~4-6h over 3 days
    "frequent":       (1, 60, (12, 20)),             # ~hourly over 24h
    "continuous":     (0.25, 10, (10, 15)),          # every ~10-15 min over last 6h
}


def attributes_for(data_point: str) -> dict:
    key = data_point.lower()
    for keyword, attributes in RAW_ATTRIBUTE_PROFILES.items():
        if keyword in key:
            return attributes
    return DEFAULT_ATTRIBUTES


def value_generator_for(data_point: str):
    key = data_point.lower()

    if "temperature" in key:
        return lambda: f"{round(random.uniform(18, 26), 1)}°C"
    if "humidity" in key:
        return lambda: f"{round(random.uniform(30, 60), 1)}%"
    if "video" in key or "image" in key:
        return lambda: "1 frame captured"
    if "presence" in key or "occupancy" in key or "localisation" in key:
        return lambda: random.choice(["Occupied", "Vacant"])
    if "identity" in key or "access timestamps" in key:
        return lambda: f"Badge #{random.randint(1000, 9999)}"
    if "plate identifier" in key:
        return lambda: f"Plate {random.choice('ABCDEFGH')}{random.randint(100, 999)}"
    if "electricity" in key:
        return lambda: f"{round(random.uniform(0.1, 3.5), 2)} kWh"
    if "water" in key:
        return lambda: f"{round(random.uniform(0.5, 8.0), 2)} L"
    if "environmental" in key:
        return lambda: f"{round(random.uniform(15, 30), 1)}°C ambient"
    if "event location" in key:
        return lambda: random.choice(["Zone A", "Zone B", "Zone C"])

    return lambda: "N/A"


def instances_for_device_type(device_type):
    raw = device_type.primary_data_collected or "General data"
    points = [p.strip() for p in raw.split(",") if p.strip()]
    return points if points else ["General data"]


def generate_samples(instance, data_point, collection_frequency: str):
    value_generator = value_generator_for(data_point)
    window_days, spacing_minutes, count_range = FREQUENCY_TO_SAMPLING[collection_frequency]
    sample_count = random.randint(*count_range)
    window_minutes = window_days * 24 * 60

    for _ in range(sample_count):
        if spacing_minutes is None:
            minutes_ago = random.randint(0, int(window_minutes))
        else:
            minutes_ago = min(
                int(window_minutes),
                max(0, random.randint(0, int(window_minutes // max(1, spacing_minutes))) * spacing_minutes
                    + random.randint(-spacing_minutes // 3, spacing_minutes // 3))
            )

        db.session.add(DeviceDataSample(
            data_value=value_generator(),
            captured_at=datetime.now(timezone.utc) - timedelta(minutes=minutes_ago),
            id_instance=instance.id_instance,
        ))


def seed():
    app = create_app()
    with app.app_context():
        factors_by_name = {f.name: f for f in RiskFactor.query.filter_by(is_deleted=False).all()}
        if len(factors_by_name) != 7:
            print(f"Expected 7 RiskFactor rows, found {len(factors_by_name)}. Run seed_reference_data.py first.")
            return

        devices = Device.query.filter_by(is_deleted=False).all()

        for device in devices:
            existing = CollectionInstance.query.filter_by(id_device=device.id_device).count()
            if existing > 0:
                continue

            if device.device_type is None:
                continue

            data_points = instances_for_device_type(device.device_type)

            for data_point in data_points:
                attributes = attributes_for(data_point)

                instance = CollectionInstance(
                    data_description=data_point,
                    id_device=device.id_device,
                    data_nature=attributes["data_nature"],
                    identifiability_level=attributes["identifiability_level"],
                    location_scope=attributes["location_scope"],
                    collection_frequency=attributes["collection_frequency"],
                    access_scope=attributes["access_scope"],
                    sharing_scope=attributes["sharing_scope"],
                )
                db.session.add(instance)
                db.session.flush()

                try:
                    ratings = compute_factor_ratings(instance)
                except InvalidAttributeError as e:
                    print(f"Skipping instance '{data_point}' on device '{device.name}': {e}")
                    db.session.rollback()
                    continue

                for factor_name, rating in ratings.items():
                    factor = factors_by_name.get(factor_name)
                    if factor:
                        db.session.add(InstanceFactorScore(
                            rating=rating,
                            id_instance=instance.id_instance,
                            id_factor=factor.id_factor,
                        ))

                generate_samples(instance, data_point, attributes["collection_frequency"])

        db.session.commit()
        print("Simulated collection instances, factor ratings, and data samples seeded.")


if __name__ == "__main__":
    seed()