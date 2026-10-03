from app import create_app, db
from app.models import RiskFactor, FactorGroup, BmsSubsystem, DeviceType

"""
Purpose: One-time script to populate reference/configuration tables:
FactorGroup, RiskFactor (grounded in Section 3.2/3.3 of the conference
paper), and BmsSubsystem + DeviceType (grounded in Figure 3, "Table of
smart building devices by BMS subsystem").

Subsystems and device types are get-or-create by name, so re-running
this script never duplicates entries you already created manually
through the UI (e.g. an existing "HVAC" subsystem is reused, not
recreated).

How to run it:
    docker compose exec backend python seed_reference_data.py
"""

GROUPS = ["impact", "likelihood"]

# (name, group_name) — Section 3.3.3 of the paper
FACTORS = [
    ("Data type", "impact"),
    ("Sensitivity", "impact"),
    ("Identifiability", "impact"),
    ("Location tracking", "impact"),
    ("Frequency of collection", "likelihood"),
    ("Access control", "likelihood"),
    ("Data sharing", "likelihood"),
]

# (subsystem_name, [(device_type_name, primary_data_collected), ...]) — Figure 3
SUBSYSTEMS = [
    ("HVAC", [
        ("Central thermostat", "Temperature, humidity, inferred presence"),
        ("Temperature/humidity sensor", "Temperature, humidity"),
        ("Air handling unit sensor", "Temperature, humidity, inferred presence"),
    ]),
    ("Lighting", [
        ("Occupancy-linked light sensor", "Presence, zone occupancy"),
        ("Automated dimming controller", "Presence, zone occupancy"),
    ]),
    ("Security", [
        ("CCTV camera", "Video/image"),
        ("RFID badge reader", "Identity, access timestamps"),
        ("Smart lock", "Access timestamps"),
        ("Intrusion detector", "Environmental data, event location"),
    ]),
    ("Fire & life safety", [
        ("Connected smoke/heat detector", "Environmental data, event location"),
        ("Gas sensor", "Environmental data, event location"),
    ]),
    ("Electrical", [
        ("Smart energy meter", "Electricity consumption (high frequency)"),
        ("Zone-level consumption sensor", "Electricity consumption (high frequency)"),
    ]),
    ("Water management", [
        ("Smart water leak detector", "Water consumption"),
        ("Water meter", "Water consumption"),
    ]),
    ("Parking", [
        ("Parking occupancy sensor", "Vehicle presence"),
        ("LPR camera", "Vehicle presence, plate identifier"),
    ]),
    ("Occupancy (cross-subsystem)", [
        ("PIR sensor", "Presence, indoor localisation"),
        ("People-counting sensor", "Presence, indoor localisation"),
    ]),
]


def seed():
    app = create_app()
    with app.app_context():
        # ---- Factor groups + risk factors ----
        group_map = {}
        for name in GROUPS:
            group = FactorGroup.query.filter_by(name=name).first()
            if group is None:
                group = FactorGroup(name=name)
                db.session.add(group)
                db.session.flush()
            group_map[name] = group.id_factor_group

        for name, group_name in FACTORS:
            existing = RiskFactor.query.filter_by(name=name, is_deleted=False).first()
            if existing is None:
                db.session.add(RiskFactor(name=name, id_factor_group=group_map[group_name]))

        # ---- BMS subsystems + device types (get-or-create by name) ----
        for subsystem_name, device_types in SUBSYSTEMS:
            subsystem = BmsSubsystem.query.filter_by(name=subsystem_name, is_deleted=False).first()
            if subsystem is None:
                subsystem = BmsSubsystem(name=subsystem_name, is_deleted=False)
                db.session.add(subsystem)
                db.session.flush()

            for type_name, primary_data in device_types:
                existing_type = DeviceType.query.filter_by(
                    name=type_name, id_subsystem=subsystem.id_subsystem, is_deleted=False
                ).first()
                if existing_type is None:
                    db.session.add(DeviceType(
                        name=type_name,
                        primary_data_collected=primary_data,
                        id_subsystem=subsystem.id_subsystem,
                        is_deleted=False
                    ))

        db.session.commit()
        print("Reference data seeded (factor groups, risk factors, BMS subsystems, device types).")


if __name__ == "__main__":
    seed()