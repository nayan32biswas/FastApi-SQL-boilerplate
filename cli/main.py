# import asyncio

import typer
from email_validator import validate_email

from app.core.db.session import get_sync_session
from app.user.models_manager.user import UserManager

app = typer.Typer()


@app.command()
def create_user(email: str, full_name: str, password: str, is_super_admin: bool = False):
    try:
        validate_email(email)
    except Exception as e:
        raise ValueError("Email address is not valid") from e

    with get_sync_session() as session:
        user_manager = UserManager(session)

        if is_super_admin:
            _ = user_manager.create_super_admin(
                email=email, full_name=full_name, text_password=password
            )
            print("Super admin created")
        else:
            _ = user_manager.create_public_user(
                email=email, full_name=full_name, text_password=password
            )
            print("User created")


if __name__ == "__main__":
    app()
