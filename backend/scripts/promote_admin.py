"""
Promotes an existing user to admin, gating the reference-data write
endpoints (stations/trains/routes/route-stations -- see
app/api/dependencies.require_admin). There's no API for this and no
bootstrap admin created by the migration on purpose: run this manually
against the target database after the user has registered normally.

Usage:
    python scripts/promote_admin.py someone@example.com
"""
import asyncio
import sys

# Windows fix for psycopg async
if sys.platform == "win32":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from app.db.database import AsyncSessionLocal
from app.repositories.user_repository import UserRepository


async def main(email: str):
    async with AsyncSessionLocal() as db:
        repository = UserRepository(db)
        user = await repository.get_by_email(email)

        if user is None:
            print(f"No user found for {email!r}.")
            return

        if user.is_admin:
            print(f"{email} is already an admin.")
            return

        user.is_admin = True
        await db.commit()
        print(f"Promoted {email} to admin.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/promote_admin.py <email>")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
