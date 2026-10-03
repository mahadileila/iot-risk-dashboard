import random
from datetime import datetime, timedelta, timezone
from app import create_app, db
from app.models import Device, RiskScoreHistory
from app.services.risk_scoring import compute_device_score

"""
Purpose: Generate simulated RiskScoreHistory snapshots for the past 30
days, for every device that doesn't already have history entries. Each
day gets one snapshot, produced as a small random walk around the
device's current live score — this is synthetic data for demo/chart
purposes, not a reconstruction of real past states (the app does not
track how instance ratings changed over time).

Safe to re-run: skips any device that already has history entries.

Run order (after devices and their instances/ratings already exist):
    docker compose exec backend python seed_score_history.py
"""

DAYS_OF_HISTORY = 30


def seed():
    app = create_app()
    with app.app_context():
        devices = Device.query.filter_by(is_deleted=False).all()

        for device in devices:
            existing = RiskScoreHistory.query.filter_by(id_device=device.id_device).count()
            if existing > 0:
                continue

            current_score, current_classification = compute_device_score(device.id_device)

            # Random walk backwards from today's live score, so the most
            # recent snapshot roughly matches what the device shows now.
            walking_score = current_score

            for days_ago in range(DAYS_OF_HISTORY, -1, -1):
                snapshot_date = datetime.now(timezone.utc) - timedelta(days=days_ago)

                if days_ago > 0:
                    drift = random.uniform(-4, 4)
                    walking_score = max(0.0, min(100.0, walking_score + drift))
                    score_for_day = round(walking_score, 2)
                else:
                    score_for_day = current_score  # today = the real live score

                if score_for_day == 0:
                    label = "No Risk"
                elif score_for_day <= 33:
                    label = "Low"
                elif score_for_day <= 66:
                    label = "Medium"
                else:
                    label = "High"

                db.session.add(RiskScoreHistory(
                    score=score_for_day,
                    classification=label,
                    computed_at=snapshot_date,
                    id_device=device.id_device,
                ))

        db.session.commit()
        print(f"Score history seeded ({DAYS_OF_HISTORY} days per device).")


if __name__ == "__main__":
    seed()