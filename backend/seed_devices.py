from app import create_app, db
from app.models import Device, DeviceType

"""
Purpose: Populate the Device table with a larger, realistic set of
devices (default: ~50) spread across every DeviceType seeded by
seed_reference_data.py (Figure 3 of the conference paper). This gives
the dashboard enough data to be meaningful, and gives
seed_simulated_data.py something to generate collection instances and
factor scores for.

Devices are get-or-create by name, so re-running this script is safe
and won't create duplicates — it only tops up toward the target count.

Run order:
    1. seed_reference_data.py   (subsystems, device types, risk factors)
    2. seed_devices.py          (this script)
    3. seed_simulated_data.py   (instances, factor scores, data samples)

How to run it:
    docker compose exec backend python seed_devices.py
"""

TARGET_DEVICE_COUNT = 50

# Building locations used to generate distinct, realistic device names
# per type (e.g. "CCTV camera - Lobby West").
LOCATIONS = [
    "Lobby West", "Lobby East", "Floor 1", "Floor 2", "Floor 3",
    "Floor 4", "Basement", "Server Room", "Parking Level 1",
    "Parking Level 2", "Corridor A", "Corridor B", "Rooftop",
]


def seed():
    app = create_app()
    with app.app_context():
        device_types = DeviceType.query.filter_by(is_deleted=False).all()
        if not device_types:
            print("No device types found. Run seed_reference_data.py first.")
            return

        existing_count = Device.query.filter_by(is_deleted=False).count()
        remaining = TARGET_DEVICE_COUNT - existing_count

        if remaining <= 0:
            print(f"Already have {existing_count} device(s), target of {TARGET_DEVICE_COUNT} reached. Nothing to do.")
            return

        created_count = 0
        location_index = 0

        # Cycle through device types repeatedly, pairing each with a new
        # location each time, until the target count is reached.
        while created_count < remaining:
            for device_type in device_types:
                if created_count >= remaining:
                    break

                location = LOCATIONS[location_index % len(LOCATIONS)]
                location_index += 1
                device_name = f"{device_type.name} - {location}"

                existing = Device.query.filter_by(name=device_name, is_deleted=False).first()
                if existing is not None:
                    continue

                db.session.add(Device(name=device_name, id_device_type=device_type.id_device_type))
                created_count += 1

        db.session.commit()
        print(f"{created_count} device(s) created ({existing_count + created_count} total).")


if __name__ == "__main__":
    seed()