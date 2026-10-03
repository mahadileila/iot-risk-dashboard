# 🛡️ RiskGuard IoT

A dashboard that scores the privacy risk of IoT devices in smart buildings: cameras, badge readers, occupancy sensors, smart meters,...

I built this during my research internship at UNITEN, as the working prototype behind a conference paper on privacy risk assessment for IoT-based building management systems.

Most BMS platforms care about energy and uptime, not about how much personal data is quietly being collected on the people inside the building. That's the gap this project tries to cover: for every device, what does it collect, how sensitive is it, and what's the risk score, with the reasoning behind that score fully visible, not a black box.

⚠️ This is a research prototype, not a production security tool. The devices and their data are simulated (see below).

## 📐 How the scoring works

A device can have several **collection instances**, separate data streams it produces. A camera, for example, might have a video feed instance and a motion-log instance.

Each instance is rated on 7 privacy factors, split into two groups:

- **Impact**: Data type, Sensitivity, Identifiability, Location tracking
- **Likelihood**: Frequency, Access control, Data sharing

Each factor gets a 0–4 rating from a fixed rubric, derived from 6 raw attributes of the data stream. In real life these would come from an external governance system; here they're simulated, but the scoring logic itself is real.
Score(instance) = (mean(Impact) × mean(Likelihood) / 16) × 100
Score(device) = MAX of its instance scores


Then classified: 🟢 Low (0–33.99) · 🟠 Medium (34–66.99) · 🔴 High (67–100)

## 🧰 Stack

**Frontend** Angular (standalone, zoneless) · Tailwind · Chart.js
**Backend** Flask · Flask-SQLAlchemy · Flask-Migrate
**DB** SQLite
**Auth** JWT
**Infra** Docker · Nginx

## ✨ Features

- Full CRUD on subsystems, device types and devices
- Device detail view with every collection instance, its raw attributes, factor ratings and sample data, fully traceable scoring
- Dashboard: summary cards, risk-by-subsystem chart, risk-over-time chart
- CSV export
- JWT login protecting the whole app

## 🚀 Running it

Needs Docker Desktop.

```bash
cp backend/.env.example backend/.env
# generate a password hash and paste it into ADMIN_PASSWORD_HASH
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"

docker compose up --build

# in another terminal
docker compose exec backend flask db upgrade
docker compose exec backend python seed_reference_data.py
docker compose exec backend python seed_devices.py
docker compose exec backend python seed_simulated_data.py
docker compose exec backend python seed_score_history.py
```

Then open `http://localhost:4200` and log in with your `.env` admin credentials.
---
Built by Leila Mahadi — research internship at UNITEN 🎓
