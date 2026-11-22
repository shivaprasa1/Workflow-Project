
from sqlalchemy import select

from app.database.database import SessionLocal
from app.models.user import User


def create_admin():

    email = input(
        "Enter the registered employee email to promote to Admin: "
    ).strip().lower()

    db = SessionLocal()

    try:

        employee = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if employee is None:

            print("Employee not found. Register the employee first.")
            return

        if employee.role == "ADMIN":

            print("This account is already an Admin.")
            return

        employee.role = "ADMIN"

        db.commit()

        print(f"{employee.email} is now an Admin.")

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":
    create_admin()
