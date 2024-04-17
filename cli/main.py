# import asyncio

import typer
from pydantic import EmailStr

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def create_user(email: EmailStr, password: str, is_admin: bool = False):
    print(f"{email=} {is_admin=}")
    if is_admin:
        # asyncio.run(create_admin_user(email=email, password=password))
        print("Admin created")
    else:
        # asyncio.run(create_public_user(email=email, password=password))
        print("Public user created")


if __name__ == "__main__":
    app()
