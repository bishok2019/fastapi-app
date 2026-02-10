from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from apps.authentication.authentication import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_current_user,
    verify_token,
)
from apps.authentication.models import User
from apps.authentication.schemas import UserCreate, UserLogin, UserRetrieve
from apps.authentication.utils import hash_password, verify_password
from apps.blog.schemas import PostList
from apps.database import get_db
from base.route import StandardResponse

router = APIRouter()


@router.post("/register", response_model=StandardResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
    )
    if existing_user:
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail="Username or email already registered",
        # )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=StandardResponse.error_response(
                message="Username or email already registered"
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

    # return StandardResponse(
    #     success=True,
    #     data={
    #         "id": db_user.id,
    #         "username": db_user.username,
    #         "email": db_user.email,
    #     },
    #     message="User registered successfully",
    # )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=StandardResponse.success_response(
            data={
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
            },
            message="User registered successfully",
        ).model_dump(),
    )


@router.post("/login")
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT tokens"""
    # Find user
    user = db.query(User).filter(User.username == user_credentials.username).first()

    if not user or not verify_password(user_credentials.password, user.hashed_password):
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Invalid username or password",
        #     headers={"WWW-Authenticate": "Bearer"},
        # )
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=StandardResponse.error_response(
                message="Invalid username or password"
            ).model_dump(),
        )

    if not user.is_active:
        # raise HTTPException(
        #     status_code=status.HTTP_400_BAD_REQUEST,
        #     detail="Inactive user account",
        # )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=StandardResponse.error_response(
                message="Inactive user account"
            ).model_dump(),
        )

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # return StandardResponse(
    #     success=True,
    #     data={
    #         "access_token": access_token,
    #         "refresh_token": refresh_token,
    #         "token_type": "bearer",
    #         "user": {
    #             "id": user.id,
    #             "username": user.username,
    #             "email": user.email,
    #         },
    #     },
    #     message="Login successful",
    # )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            message="Login successful",
        ).model_dump(),
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client-side token removal)"""
    # return StandardResponse(
    #     success=True,
    #     data=None,
    #     message="Logout successful. Please remove token from client.",
    # )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data=None,
            message="Logout successful. Please remove token from client.",
        ).model_dump(),
    )


@router.get("/profile")
def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user"""
    # return StandardResponse.success_response(
    #     data={
    #         "id": current_user.id,
    #         "username": current_user.username,
    #         "email": current_user.email,
    #         "is_active": current_user.is_active,
    #         "posts": [PostList.model_validate(post) for post in current_user.posts],
    #     },
    #     message="User Profile retrieved successfully",
    # )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            data={
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "is_active": current_user.is_active,
                "posts": [PostList.model_validate(post) for post in current_user.posts],
            },
            message="User Profile retrieved successfully",
        ).model_dump(),
    )


@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        user_id = verify_token(refresh_token)
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            # return StandardResponse.error_response(
            #     message="User not found",
            #     status_code=status.HTTP_404_NOT_FOUND,
            # )
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=StandardResponse.error_response(
                    message="User not found"
                ).model_dump(),
            )

        # Create new access token
        new_access_token = create_access_token(data={"sub": str(user.id)})

        # return StandardResponse.success_response(
        #     data={
        #         "access_token": new_access_token,
        #         "token_type": "bearer",
        #     },
        #     message="Token refreshed successfully",
        # )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=StandardResponse.success_response(
                data={
                    "access_token": new_access_token,
                    "token_type": "bearer",
                },
                message="Token refreshed successfully",
            ).model_dump(),
        )
    # except HTTPException:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid refresh token",
    #     )
    except HTTPException:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=StandardResponse.error_response(
                message="Invalid refresh token"
            ).model_dump(),
        )


@router.post("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change user password"""
    # Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        # return StandardResponse.error_response(
        #     message="Current password is incorrect",
        #     status_code=status.HTTP_400_BAD_REQUEST,
        # )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=StandardResponse.error_response(
                message="Current password is incorrect"
            ).model_dump(),
        )

    # Update password
    current_user.hashed_password = hash_password(new_password)
    db.commit()

    # return StandardResponse.success_response(message="Password changed successfully")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=StandardResponse.success_response(
            message="Password changed successfully"
        ).model_dump(),
    )
