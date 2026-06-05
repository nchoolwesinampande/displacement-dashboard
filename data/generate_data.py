"""
Sample data generator for the Beneficiary Solutions Dashboard.

This produces an *internally coherent* synthetic dataset rather than independent
random draws, so the dashboard tells a sensible story:

  * Solutions pathways respect displacement status
      - Returnees and host-community members are reintegrated locally
        (Local Integration), not assigned a "Return" pathway they have already
        completed; only IDPs can take any of the three pathways.
  * Progress is a real funnel (Assessment > Planning > Implementation > Achieved)
    driven by how long ago a household was registered: earlier cohorts have had
    time to advance, recent intake sits at Assessment.
  * Shelter, documentation and livelihood support all improve with the pathway
    stage, so an "Achieved" durable solution implies permanent shelter and
    complete civil documentation, while a household still in "Assessment" does
    not.
  * Achievement varies by region to reflect differing operational contexts.
  * Coordinates fall near the real centroid of each district.

Run with: python data/generate_data.py
Output:   data/sample_data.csv  (reproducible via the fixed seed)
"""

import os
import numpy as np
import pandas as pd

SEED = 42
N = 800
START = pd.Timestamp("2022-06-01")
END = pd.Timestamp("2024-12-31")

# Region -> districts, each district with an approximate real centroid (lat, lon).
GEO = {
    "Baidoa": {
        "Baidoa Central": (3.114, 43.650),
        "Buur Hakaba": (2.780, 44.070),
        "Dinsor": (2.402, 42.972),
    },
    "Dollow": {
        "Dollow Town": (4.160, 42.073),
        "Luuq": (3.804, 42.544),
    },
    "Garowe": {
        "Garowe Central": (8.404, 48.482),
        "Burtinle": (7.871, 47.990),
    },
    "Kismayo": {
        "Kismayo Central": (-0.358, 42.545),
        "Badhadhe": (-0.360, 41.710),
    },
    "Mogadishu": {
        "Hodan": (2.040, 45.310),
        "Yaqshid": (2.072, 45.343),
        "Wadajir": (2.022, 45.300),
    },
}

# Relative caseload by region.
REGION_WEIGHTS = {
    "Baidoa": 0.26,
    "Mogadishu": 0.24,
    "Kismayo": 0.18,
    "Dollow": 0.18,
    "Garowe": 0.14,
}

# Operational context: how much further along a region's caseload tends to be.
REGION_PROGRESS = {
    "Garowe": 0.12,    # Puntland, comparatively stable
    "Dollow": 0.04,
    "Mogadishu": 0.00,
    "Kismayo": -0.03,
    "Baidoa": -0.09,   # protracted IDP situation
}

STAGES = ["Assessment", "Planning", "Implementation", "Achieved"]

# Conditional distributions keyed by pathway stage (index aligned to STAGES).
SHELTER_BY_STAGE = {
    "Assessment": [("Emergency", 0.75), ("Transitional", 0.22), ("Permanent", 0.03)],
    "Planning": [("Emergency", 0.45), ("Transitional", 0.45), ("Permanent", 0.10)],
    "Implementation": [("Emergency", 0.12), ("Transitional", 0.55), ("Permanent", 0.33)],
    "Achieved": [("Emergency", 0.00), ("Transitional", 0.15), ("Permanent", 0.85)],
}
DOC_BY_STAGE = {
    "Assessment": [("None", 0.60), ("Partial", 0.33), ("Complete", 0.07)],
    "Planning": [("None", 0.33), ("Partial", 0.47), ("Complete", 0.20)],
    "Implementation": [("None", 0.12), ("Partial", 0.45), ("Complete", 0.43)],
    "Achieved": [("None", 0.00), ("Partial", 0.12), ("Complete", 0.88)],
}
LIVELIHOOD_YES_BY_STAGE = {
    "Assessment": 0.08,
    "Planning": 0.30,
    "Implementation": 0.62,
    "Achieved": 0.85,
}
# Pathway depends on displacement status.
PATHWAY_BY_STATUS = {
    "IDP": [("Return", 0.35), ("Local Integration", 0.40), ("Relocation", 0.25)],
    "Returnee": [("Local Integration", 0.82), ("Relocation", 0.12), ("Return", 0.06)],
    "Host Community": [("Local Integration", 1.00)],
}
STATUS_WEIGHTS = [("IDP", 0.62), ("Returnee", 0.23), ("Host Community", 0.15)]


def pick(rng, choices):
    """Sample one label from a list of (label, weight) pairs."""
    labels = [c[0] for c in choices]
    weights = np.array([c[1] for c in choices], dtype=float)
    weights /= weights.sum()
    return rng.choice(labels, p=weights)


def main():
    rng = np.random.default_rng(SEED)
    span_days = (END - START).days

    rows = []
    for i in range(N):
        # Region / district / coordinates.
        region = pick(rng, list(REGION_WEIGHTS.items()))
        district = rng.choice(list(GEO[region].keys()))
        base_lat, base_lon = GEO[region][district]
        lat = round(base_lat + rng.normal(0, 0.045), 4)
        lon = round(base_lon + rng.normal(0, 0.045), 4)

        # Registration date: programme intake ramps up over time, so recent
        # cohorts dominate and the funnel stays realistic.
        frac = rng.beta(1.6, 1.4)  # mild skew toward 1.0 (recent)
        reg_date = START + pd.Timedelta(days=int(frac * span_days))
        tenure_frac = 1.0 - frac  # 1.0 = registered at the very start

        # Latent progress: longer tenure + regional context + noise.
        latent = tenure_frac + REGION_PROGRESS[region] + rng.normal(0, 0.12)
        if latent < 0.34:
            stage = "Assessment"
        elif latent < 0.60:
            stage = "Planning"
        elif latent < 0.80:
            stage = "Implementation"
        else:
            stage = "Achieved"

        # Status -> pathway (coherent).
        status = pick(rng, STATUS_WEIGHTS)
        pathway = pick(rng, PATHWAY_BY_STATUS[status])

        # Stage -> shelter / documentation / livelihood.
        shelter = pick(rng, SHELTER_BY_STAGE[stage])
        documentation = pick(rng, DOC_BY_STAGE[stage])
        livelihood = "Yes" if rng.random() < LIVELIHOOD_YES_BY_STAGE[stage] else "No"

        # Demographics.
        gender = "Female" if rng.random() < 0.40 else "Male"
        household_size = int(np.clip(round(rng.gamma(shape=4.2, scale=1.5)), 1, 14))

        rows.append(
            {
                "beneficiary_id": f"BEN-{i + 1:04d}",
                "registration_date": reg_date.strftime("%Y-%m-%d"),
                "region": region,
                "district": district,
                "displacement_status": status,
                "solutions_pathway": pathway,
                "pathway_stage": stage,
                "household_size": household_size,
                "gender_hoh": gender,
                "shelter_status": shelter,
                "livelihood_support": livelihood,
                "documentation_status": documentation,
                "latitude": lat,
                "longitude": lon,
            }
        )

    df = pd.DataFrame(rows).sort_values("registration_date").reset_index(drop=True)
    # Re-number IDs in chronological order for a tidy dataset.
    df["beneficiary_id"] = [f"BEN-{i + 1:04d}" for i in range(len(df))]

    out_path = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()
