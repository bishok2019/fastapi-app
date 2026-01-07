# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session

# from apps.database import get_db
# from base.route import (
#     CreateRouter,
#     ReadRouter,
#     RetrieveRouter,
#     StandardResponse,
#     UpdateRouter,
# )

# from .models.models import User
# from .schemas import UserCreate, UserList, UserLogin, UserRetrieve, UserUpdate
# from .utils import hash_password, verify_password

# router = APIRouter()


# class UserCreateRouter(CreateRouter[User, UserCreate]):
#     def create(self, item: UserCreate, db: Session = Depends(get_db)):
#         # Check if user exists already
#         if (
#             db.query(self.model)
#             .filter(
#                 (self.model.username == item.username)
#                 | (self.model.email == item.email)
#             )
#             .first()
#         ):
#             raise HTTPException(
#                 status_code=400, detail="Username or email already registered."
#             )
#         db_item = self.model(
#             username=item.username,
#             email=item.email,
#             hashed_password=hash_password(item.password),
#         )
#         db.add(db_item)
#         db.commit()
#         db.refresh(db_item)
#         return StandardResponse(
#             success=True,
#             data=self.schema.model_validate(db_item),
#             message="User created successfully.",
#         )


# class UserReadRouter(ReadRouter[User, UserList]):
#     def read_all(self, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#         items = db.query(self.model).offset(skip).limit(limit).all()
#         data = [self.schema.model_validate(item) for item in items]
#         return StandardResponse(
#             success=True, data=data, message="Users fetched successfully."
#         )


# class UserRetrieveRouter(RetrieveRouter[User, UserRetrieve]):
#     def retrieve(self, user_id: int, db: Session = Depends(get_db)):
#         db_item = db.query(self.model).filter(self.model.id == user_id).first()
#         if not db_item:
#             raise HTTPException(status_code=404, detail="User not found.")
#         return StandardResponse(
#             success=True,
#             data=self.schema.model_validate(db_item),
#             message="User retrieved successfully.",
#         )


# @router.post("/login")
# def login(user: UserLogin, db: Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.username == user.username).first()
#     if not db_user or not verify_password(user.password, db_user.hashed_password):
#         raise HTTPException(status_code=401, detail="Invalid username or password.")
#     return {"message": "Login successful.", "username": db_user.username}

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.database import get_db
from base.pagination import paginate
from base.route import StandardResponse

from .models.models import User
from .schemas import UserCreate, UserList, UserLogin, UserRetrieve, UserUpdate
from .utils import hash_password, verify_password

router = APIRouter()


@router.post(
    "/create", response_model=StandardResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if user exists already
    existing_user = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )
    if existing_user:
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail="Username or email already registered.",
        # )
        # return StandardResponse.error_response(
        #     message="Username or email already registered.",
        #     status_code=status.HTTP_400_BAD_REQUEST,
        # )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=StandardResponse.error_response(
                message="Username or email already registered."
            ).model_dump(),
        )

    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        is_active=True,
        is_superuser=False,
        # is_verified=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=StandardResponse.success_response(
            data=UserRetrieve.model_validate(db_user),
            message="User created successfully.",
        ).model_dump(),
    )


@router.get("/list", response_model=StandardResponse)
def get_users(
    page: int = 1,  # we are passing page and page_size in paginate() directly
    page_size: int = 1,
    db: Session = Depends(get_db),
):
    """Get all users with pagination"""
    # users = db.query(User).all()
    # data = [UserList.model_validate(user) for user in users]
    result = paginate(
        query=db.query(User),
        page=page,  # we are passing page and page_size in paginate() directly
        page_size=page_size,
        schema=UserList,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=result.data,
            message="Users fetched successfully.",
            meta=result.meta,
        ).model_dump(),
    )
    # return JSONResponse(
    #     status_code=status.HTTP_200_OK,
    #     content=StandardResponse.success_response(
    #         data=data,
    #         message="Users fetched successfully.",
    #     ).model_dump(),
    # )


@router.get("/retrieve/{user_id}", response_model=StandardResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=StandardResponse.error_response(
                message="User not found.",
            ).model_dump(),
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=UserRetrieve.model_validate(user),
            message="User retrieved successfully.",
        ).model_dump(),
    )
