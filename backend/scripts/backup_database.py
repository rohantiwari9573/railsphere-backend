"""
Dumps the database with pg_dump, gzips it, and prunes backups older
than BACKUP_RETENTION_DAYS. Run manually, or on a schedule via
deploy/railsphere-backup.service + .timer.

Local-disk only for now -- protects against a bad migration, a
mistaken DELETE, or other application/DB-level accidents (restore
without needing the instance to survive), but not against loss of the
instance or its EBS volume. Upgrading to off-instance (S3) backups
just means pointing the upload step below at a bucket once an IAM
role/credentials for it exist -- the dump/prune logic doesn't change.
"""

import gzip
import shutil
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402

BACKUP_DIR = Path(__file__).resolve().parent.parent / "backups"
RETENTION_DAYS = 7


def _pg_dump_args() -> list[str]:
    # DATABASE_URL is postgresql+psycopg://user:pass@host:port/dbname --
    # pg_dump wants a plain postgresql:// URL, not the +psycopg variant.
    parsed = urlparse(settings.DATABASE_URL.replace("+psycopg", ""))
    return [
        "pg_dump",
        "--host", parsed.hostname or "localhost",
        "--port", str(parsed.port or 5432),
        "--username", parsed.username or "postgres",
        "--no-password",
        "--format", "plain",
        parsed.path.lstrip("/"),
    ]


def run_backup() -> Path:
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    dest = BACKUP_DIR / f"railsphere-{timestamp}.sql.gz"

    env = {}
    parsed = urlparse(settings.DATABASE_URL.replace("+psycopg", ""))
    if parsed.password:
        env["PGPASSWORD"] = parsed.password

    result = subprocess.run(
        _pg_dump_args(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"pg_dump failed (exit {result.returncode}): "
            f"{result.stderr.decode(errors='replace')}"
        )
    with gzip.open(dest, "wb") as gz_out:
        gz_out.write(result.stdout)

    size_mb = dest.stat().st_size / (1024 * 1024)
    print(f"Wrote {dest} ({size_mb:.1f} MB)")
    return dest


def prune_old_backups() -> None:
    cutoff = datetime.now(UTC) - timedelta(days=RETENTION_DAYS)
    for path in BACKUP_DIR.glob("railsphere-*.sql.gz"):
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
        if mtime < cutoff:
            path.unlink()
            print(f"Pruned {path.name} (older than {RETENTION_DAYS} days)")


def disk_usage_summary() -> None:
    total_bytes = sum(p.stat().st_size for p in BACKUP_DIR.glob("*.sql.gz"))
    count = len(list(BACKUP_DIR.glob("*.sql.gz")))
    free_bytes = shutil.disk_usage(BACKUP_DIR).free
    print(
        f"{count} backup(s), {total_bytes / (1024 * 1024):.1f} MB total, "
        f"{free_bytes / (1024 * 1024 * 1024):.1f} GB free on disk"
    )


if __name__ == "__main__":
    run_backup()
    prune_old_backups()
    disk_usage_summary()
