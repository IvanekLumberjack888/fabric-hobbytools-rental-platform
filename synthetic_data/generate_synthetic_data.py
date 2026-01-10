
## Skeleton `generate_synthetic_data.py`

```python
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

np.random.seed(42)

OUTPUT_DIR = Path("synthetic_data")
OUTPUT_DIR.mkdir(exist_ok=True)

locations = ["Prague", "Brno", "Ostrava"]
tool_categories = ["pressure_washer", "drill", "grinder", "saw"]
tool_names = {
    "pressure_washer": ["Karcher K5", "Karcher K7"],
    "drill": ["Bosch Pro Drill", "Makita Hammer Drill"],
    "grinder": ["Metabo Angle Grinder", "Bosch Grinder"],
    "saw": ["Makita Circular Saw", "DeWalt Jigsaw"],
}

def generate_tools(n_tools=50):
    rows = []
    for i in range(n_tools):
        cat = np.random.choice(tool_categories)
        name = np.random.choice(tool_names[cat])
        tool_id = f"{cat[:3].upper()}_{i:03d}"
        row = {
            "tool_id": tool_id,
            "tool_category": cat,
            "tool_name": name,
            "purchase_date": (datetime.today() - timedelta(days=np.random.randint(200, 2000))).date(),
            "purchase_price_czk": float(np.random.randint(5000, 40000)),
            "current_value_czk": float(np.random.randint(1000, 30000)),
            "location": np.random.choice(locations),
            "status": np.random.choice(["available", "rented", "maintenance"]),
            "maintenance_contract": np.random.choice(["yes", "no"]),
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "bronze_tools_sample.csv", index=False)

def generate_rentals(tools_df, n_rentals=500):
    rows = []
    for i in range(n_rentals):
        tool = tools_df.sample(1).iloc[0]
        start = datetime.today() - timedelta(days=np.random.randint(1, 120))
        duration_days = np.random.randint(1, 10)
        end = start + timedelta(days=duration_days)

        daily_rate = np.random.choice([400, 600, 800, 1000])
        damage = np.random.rand() < 0.15

        row = {
            "rental_id": f"RENT-{i:05d}",
            "tool_id": tool["tool_id"],
            "customer_id": f"CUST-{np.random.randint(1, 200):04d}",
            "rental_date": start.date(),
            "return_date": end.date(),
            "daily_rate_czk": daily_rate,
            "damage_reported": damage,
            "damage_cost_czk": float(np.random.randint(0, 3000)) if damage else 0.0,
            "customer_rating": np.random.randint(2, 6),
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "bronze_rentals_sample.csv", index=False)

def generate_repairs(rentals_df, n_repairs=200):
    rows = []
    failure_types = ["motor_failure", "seal_leak", "power_issue", "other"]
    for i in range(n_repairs):
        rental = rentals_df.sample(1).iloc[0]
        repair_date = pd.to_datetime(rental["return_date"]) + timedelta(days=np.random.randint(0, 20))
        cost = np.random.randint(500, 6000)
        parts = np.random.randint(0, 3000)
        row = {
            "repair_id": f"REP-{i:05d}",
            "tool_id": rental["tool_id"],
            "rental_id": rental["rental_id"],
            "repair_date": repair_date.date(),
            "failure_type": np.random.choice(failure_types),
            "repair_cost_czk": float(cost),
            "repair_hours": float(np.random.randint(1, 8)),
            "replacement_parts_cost_czk": float(parts),
            "repair_status": np.random.choice(["in_progress", "completed", "warranty"]),
            "warranty_claim": bool(np.random.rand() < 0.3),
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "bronze_repairs_sample.csv", index=False)

def generate_staff(n_days=120):
    rows = []
    today = datetime.today().date()
    employee_ids = [f"EMP{i:03d}" for i in range(1, 25)]
    departments = ["rental", "service", "sales"]

    for day_offset in range(n_days):
        date = today - timedelta(days=day_offset)
        for emp in employee_ids:
            location = np.random.choice(locations)
            department = np.random.choice(departments, p=[0.4, 0.4, 0.2])
            is_vacation = np.random.rand() < 0.05
            is_sick = np.random.rand() < 0.03
            if is_vacation or is_sick:
                time_in = "00:00"
                time_out = "00:00"
                overtime = 0.0
            else:
                time_in = "08:00"
                time_out = np.random.choice(["16:30", "17:00", "18:00"])
                overtime = float(np.random.choice([0.0, 1.0, 2.0], p=[0.7, 0.2, 0.1]))
            row = {
                "employee_id": emp,
                "date": date,
                "location": location,
                "department": department,
                "time_in": time_in,
                "time_out": time_out,
                "overtime_hours": overtime,
                "is_vacation": is_vacation,
                "is_sick_leave": is_sick,
                "tasks": "customer_service,maintenance" if department != "sales" else "sales",
            }
            rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / "bronze_staff_sample.csv", index=False)

if __name__ == "__main__":
    print("Generating synthetic data...")
    generate_tools()
    tools_df = pd.read_csv(OUTPUT_DIR / "bronze_tools_sample.csv")
    generate_rentals(tools_df)
    rentals_df = pd.read_csv(OUTPUT_DIR / "bronze_rentals_sample.csv")
    generate_repairs(rentals_df)
    generate_staff()
    print("Done. CSV files created in synthetic_data/ directory.")
