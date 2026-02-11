from colorama import Fore
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from apps.authentication.models import (
    CustomPermission,
    CustomRole,
    PermissionCategory,
    User,
)
from apps.authentication.permissions import (
    ALL_PERMISSION_LIST,
    HttpBasedPermissionActionMaps,
    PermissionLists,
)
from apps.blog.models import Post
from apps.database import SessionLocal
from apps.notification.models import (
    Notification,
    NotificationTypeChoices,
    UserNotification,
)


def run_permission_setup():
    db: Session = SessionLocal()
    try:
        # ------------------- Existing permissions & categories -------------------
        existing_permissions_map = set(
            db.scalars(
                select(
                    CustomPermission.code_name
                )  # select() returns a list of CustomPermission objects, we only want code_name
            ).all()  # scalar() returns a list of code_names
        )

        existing_categories = {
            cat.name: cat for cat in db.scalars(select(PermissionCategory)).all()
        }

        print(Fore.BLUE + "PREPARING PERMISSION CATEGORIES...")

        # Collect unique category names from ALL_PERMISSION_LIST
        all_category_names = set()
        for app_name, models in ALL_PERMISSION_LIST.items():
            for model_name in models.keys():
                category_name = model_name.replace("_", " ").title()
                all_category_names.add(category_name)

        # Create missing categories
        new_categories = []
        for category_name in all_category_names:
            if category_name not in existing_categories:
                cat = PermissionCategory(name=category_name)
                db.add(cat)
                new_categories.append(cat)

        if new_categories:
            db.commit()  # commit to get IDs
            for cat in new_categories:
                existing_categories[cat.name] = cat
            print(
                Fore.GREEN + f"Created {len(new_categories)} new Permission Categories."
            )

        # ------------------- Create permissions -------------------
        print(Fore.BLUE + "PREPARING PERMISSIONS...\n")

        to_create_permissions = []
        for app_name, models in ALL_PERMISSION_LIST.items():
            for model_name, actions in models.items():
                category_name = model_name.replace("_", " ").title()
                category = existing_categories.get(category_name)

                for action in actions:
                    code_name = f"can_{action}_{model_name}"
                    if code_name not in existing_permissions_map:
                        readable_name = f"Can {action.title()} {model_name.replace('_', ' ').title()}"
                        perm = CustomPermission(
                            name=readable_name, code_name=code_name, category=category
                        )
                        db.add(perm)
                        to_create_permissions.append(perm)

        if to_create_permissions:
            db.commit()
            print(
                Fore.GREEN + f"Created {len(to_create_permissions)} new Permissions.\n"
            )

        # ------------------- Create support role -------------------
        support_role = db.scalar(
            select(CustomRole).where(
                CustomRole.name == PermissionLists.SUPPORT_ROLE_NAME
            )
        )
        if not support_role:
            support_role = CustomRole(
                name=PermissionLists.SUPPORT_ROLE_NAME,
                description="This Role is dedicated to VIEW Permissions Only",
                is_active=True,
            )
            db.add(support_role)
            db.commit()

        # Assign all "view" permissions to support role
        view_perms = db.scalars(
            select(CustomPermission).where(
                CustomPermission.code_name.startswith(
                    HttpBasedPermissionActionMaps.CAN_VIEW
                )
            )
        ).all()
        support_role.permissions = view_perms
        db.commit()
        print(
            Fore.GREEN
            + f"Support role '{support_role.name}' created and assigned view permissions."
        )

        # ------------------- Assign superusers -------------------
        superusers = db.scalars(select(User).where(User.is_superuser)).all()
        all_roles = db.scalars(select(CustomRole)).all()
        all_permissions = db.scalars(select(CustomPermission)).all()

        for user in superusers:
            for role in all_roles:
                if role not in user.user_roles:
                    user.user_roles.append(role)
            for perm in all_permissions:
                if perm not in user.user_permissions:
                    user.user_permissions.append(perm)

        db.commit()
        print(Fore.GREEN + "Assigned all roles and permissions to superusers.")
        print(Fore.GREEN + "Permission and category setup completed successfully!")

    except SQLAlchemyError as e:
        db.rollback()
        print(Fore.RED + f"Error occurred: {str(e)}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run_permission_setup()
