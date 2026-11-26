# Supply Chain Disruption Simulation using Monte Carlo

Interactive Streamlit application for teaching and analyzing supply-chain disruption risk using Monte Carlo simulation.

## Features
- Random disruption events
- Reduced supply during disruption
- Stochastic weekly demand
- Inventory depletion and stockouts
- Service-level and shortage analysis
- Holding and shortage cost analysis
- Monte Carlo outcome distributions
- Initial-inventory scenario analysis
- Percentile-based risk analysis
- CSV export

## Default teaching example
- Normal supply: 500 units/week
- Demand: 450 units/week
- Initial inventory: 600 units
- Disruption probability: 10% per week
- Disrupted supply: 100 units/week
- Disruption duration: 2 weeks
- Holding cost: $2/unit/week
- Shortage cost: $15/unit
- Horizon: 12 weeks
- Monte Carlo replications: 5,000

All inputs can be changed in the sidebar.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub / Streamlit Community Cloud
Upload the repository to GitHub with `app.py` and `requirements.txt`, then select this repository and `app.py` as the entrypoint in Streamlit Community Cloud.

## License
This repository is made publicly available for educational, academic, and classroom use. Permission is granted to access and use the code for learning, teaching, and academic demonstration purposes. Redistribution, commercial use, modification for public distribution, or incorporation into other projects requires prior written permission from the copyright holder, unless otherwise specified. This repository is provided "as is", without warranty of any kind. The author assumes no responsibility for any loss or damage arising from its use. For other permissions or licensing inquiries, please contact the author.
