# RailSphere Architecture

## Request flow

```
Client
  |
  v
FastAPI Router (app/api/routes/*.py)
  |
  v
Service (app/services/*.py)      <- business rules, duplicate checks, validation
  |
  v
Repository (app/repositories/*.py) <- all raw DB access lives here
  |
  v
SQLAlchemy async ORM (app/models/*.py)
  |
  v
PostgreSQL
```

Every domain (auth, stations, trains, routes, route-stations, journeys) follows this exact layering. Routes never touch the database directly; they only call a service, which only calls a repository. This is enforced by convention, not by tooling -- keep new endpoints consistent with it.

Dependency injection for all of this is wired in one place: `app/api/dependencies.py`.

## Data model

Six tables, six models:

- `users` -- auth
- `stations`, `trains`, `routes` -- independent entities, each importable/creatable on their own
- `route_stations` -- join table between routes and stations, carries `sequence_number` (position along the route), `arrival_time`/`departure_time`/`halt_minutes`. Unique on `(route_id, sequence_number)` and `(route_id, station_id)`.
- `schedules` -- join table between trains and routes (a train's run on a route), carries `start_time`/`end_time` and per-weekday boolean flags. Unique on `(train_id, route_id)`.

All FKs cascade on delete at the database level. Both `route_stations` and `schedules` had duplicate-row bugs at different points in this project's history (see the alembic history and commit log around 2026-08-19) -- both are now guarded by real unique constraints, not just application-level checks, so a bug in the app layer can't silently corrupt the data again.

## Import pipeline

`app/importers/` -- one class per dataset (`BaseImporter` subclasses), each:

1. Reads its JSON dataset (`backend/datasets/`, not versioned -- large per-environment files)
2. Loads existing keys from the DB (station codes, train numbers, route codes, or composite pairs for the join tables)
3. Skips anything already present -- every importer is safe to rerun
4. Batches inserts (500-1000 rows per commit) rather than one INSERT per row

`app/importers/import_all.py` runs all five in the correct dependency order (stations/trains/routes must exist before route_stations/schedules can reference them). `backend/scripts/import_*.py` are thin single-importer wrappers for running one dataset at a time.

## Migration history

The schema is defined by a single verified baseline migration (`c1686aac749b_initial_schema.py`) plus small incremental migrations on top (e.g., the `schedules` unique constraint). This baseline replaced an earlier, irreconcilable situation where three environments -- this dev machine, the EC2 box, and what was actually committed to GitHub -- had each generated different, incompatible migration chains. If you're ever tempted to hand-edit a migration's `down_revision` or `revision` id, don't -- that's exactly how that situation happened.

## Deployment topology (current)

```
Internet
   |
   v
EC2 (Ubuntu, single instance)
   |
   +-- nginx :80  --(reverse proxy)-->  gunicorn :127.0.0.1:8000
   |                                        |
   |                                        v
   |                                   uvicorn workers x2 (FastAPI app)
   |                                        |
   +-- PostgreSQL (native, 127.0.0.1 only, not internet-exposed)
```

No containers, no Redis, no Celery, no load balancer, no second instance. This is a single-box deployment; see the README's Deployment section and `backend/deploy/` for the actual systemd/nginx config in use.
