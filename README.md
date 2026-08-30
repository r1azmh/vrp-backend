# RouteShaper — Backend

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

RouteShaper is an open-source, web-based decision-support tool for industrial
freight route planning with integrated CO₂ emission estimation and quality
(freshness) reporting for perishable goods.

This repository contains the **backend**: a Django REST service that stores the
routing problem, calls the optimization engine, produces the route, emission
and freshness reports, and serves the compiled web interface. The interface
source lives in [vrp-frontend](https://github.com/r1azmh/vrp-frontend).

Developed at the School of Technology and Innovations, University of Vaasa,
Finland, within the project
[Optimising distribution transport in the food ecosystem](https://www.uwasa.fi/en/elintarvike-ekosysteemi).

---

## What it does

| Capability | Description |
| --- | --- |
| Route optimization | Capacitated pickup/delivery with time windows, solved by the [vrp-cli](https://github.com/reinterpretcat/vrp) (Rosomaxa) metaheuristic engine. |
| Realistic travel matrices | Distances and durations from the OpenRouteService Matrix API on the `driving-hgv` profile, so results follow the road network and HGV restrictions rather than straight-line distance. |
| CO₂ emission reporting | Per-segment emissions using load-dependent factors by truck type. |
| Freshness reporting | Per-container quality-deterioration cost from category-specific hourly penalty rates. |
| Bulk import | CSV import of jobs and fleet for industrial-scale instances. |
| Exports | Route plan and emission report as CSV. |

RouteShaper is an **integration layer**: optimization is
performed by vrp-cli and travel matrices by OpenRouteService. The contribution
is the combination of those components with emission and quality reporting
behind a practitioner-facing interface.

---

## Architecture

```
Browser ──▶ Django (serves the compiled React app + REST API)
               │
               ├──▶ vrp-cli            (optimization engine, in-process)
               ├──▶ OpenRouteService   (matrix API, driving-hgv)
               └──▶ SQLite / MySQL
```

The interface is compiled to static assets and served by Django, so a
deployment runs a single web process.

---

## Requirements

- Python 3.10.18 or newer.
- Node.js `^20.19.0` or `>=22.12.0` with Yarn, to build the interface
- An [OpenRouteService API key](https://openrouteservice.org/dev/)
- MySQL 8 only for server deployments; local installs use SQLite

---

## Installation

### 1. Backend

```bash
git clone https://github.com/r1azmh/vrp-backend.git
cd vrp-backend
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

Settings are read from environment variables via
[`environs`](https://pypi.org/project/environs/).

**Server deployment — use a `.env` file:**

```bash
cp .env.example .env
```

```ini
SECRET_KEY=<a long random string>
DEBUG=False
ORS_SECRET_KEY=<your OpenRouteService API key>
ALLOWED_HOSTS=your-domain.example
DATABASE_NAME=vrp
DATABASE_USER=vrp_user
DATABASE_PASSWORD=<password>
DATABASE_PORT=3306
```

**Local use — edit `vrp/settings.py` directly.** For a single-machine install
you may replace the two lookups with literals:

```python
SECRET_KEY = "any-non-empty-string"
ORS_SECRET_KEY = "your-openrouteservice-api-key"
```

Either way both keys must be set; Django will not start without them.

The database is selected by the `MODE` constant near the top of
`vrp/settings.py`. `MODE = "development"` (the default) uses a local SQLite
file and needs no further setup; `MODE = "production"` uses the MySQL settings
above.

`STATIC_ROOT` in `vrp/settings.py` points at the deployment host's static
directory. Change it to a path on your own machine before running
`collectstatic`.

### 3. Build the web interface

Django serves the compiled interface. The backend alone renders no pages —
`/signup/`, `/login/` and `/dashboard/` fail with `TemplateDoesNotExist` until
this step is done.

The [frontend](https://github.com/r1azmh/vrp-frontend) build writes its output **into this project directory**: Vite
emits `templates/index.html` (a Django template, with asset URLs rewritten to
`{% static %}` tags and the CSRF token injected) and the hashed bundles into
`static/`. There is no copying step.

```bash
git clone https://github.com/r1azmh/vrp-frontend.git
cd vrp-frontend
yarn install
yarn build          # writes into ../vrp-backend
```

If the two checkouts are not siblings, point the build at this directory:

```bash
VRP_BACKEND_DIR=/path/to/vrp-backend yarn build
```

Requires Node.js `^20.19.0` or `>=22.12.0`, and Yarn. Re-run `yarn build`
after any interface change; asset filenames are content-hashed, so old bundles
accumulate in `static/` and can be cleared periodically.

### 4. Initialize and run

```bash
python manage.py migrate
python manage.py runserver
```

Open `http://localhost:8000/signup/` and register an account.

If pages load blank, check the content type of `/static/main-<hash>.js`: it
must be `text/javascript`. If it comes back as `text/html`, the catch-all URL
pattern in `vrp/urls.py` is answering asset requests and needs an explicit
`static/` route placed before it. All data —
works, jobs, fleet, categories, vehicle profiles — is scoped to the account
that creates it.

---

## API reference

All endpoints require an authenticated session. Base path `/`.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `works/`, `search-works/` | List / search routing tasks |
| POST | `work-create/` | Create a routing task |
| PUT / DELETE | `work-update/<pk>/`, `work_delete/<pk>/` | Modify a task |
| GET / POST | `jobs/`, `job-create/` | Jobs (pickups / deliveries) |
| POST | `job-create-bulk/`, `fleet-create-bulk/` | CSV bulk import |
| GET / POST | `vehicles/`, `vehicle-create/` | Fleet |
| GET / POST | `vehicle-profiles/`, `vehicle-profile-create/` | Vehicle profiles |
| GET / POST | `categories/`, `category_create/` | Perishability categories |
| GET | `solve/<pk>` | Run the optimization |
| GET | `last_solution/` | Retrieve the most recent solution |
| GET | `export_solution_csv/<pk>/` | Route plan as CSV |
| GET | `emission_report/<pk>/` | Emission report (`?export_to_csv=true` for CSV) |

---

## Video Tutorial

A complete step-by-step video tutorial for installation and implementation of RouteShaper is available here:
[Tutorial Link](https://youtu.be/V_FPSygpemU).

---

## Limitations

- The OpenRouteService free tier caps matrix size and daily requests; large
  instances need a paid plan or a self-hosted ORS instance. One solve consumes
  one matrix request.
- Travel times are ORS estimates and exclude traffic, driver breaks and delays
  beyond the configured service time.
- Freshness penalties are reported but not optimized, and are not stable
  across solver runs.
- Emission factors are European diesel HGV defaults; other fleets require
  substituting the factor table.

---

## Contributing

Issues and pull requests are welcome. Please open an issue describing the
change before submitting substantial pull requests.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

Copyright © 2024–2026 Petri Helo and Riaz Mahmud.

## Acknowledgements

Supported by the European Regional Development Fund and the Regional Council
of South Ostrobothnia (grant A80384). RouteShaper builds on
[vrp-cli / Rosomaxa](https://github.com/reinterpretcat/vrp) and
[OpenRouteService](https://openrouteservice.org/) (HeiGIT).

## Contact

riaz dot mahmud at uwasa.fi 