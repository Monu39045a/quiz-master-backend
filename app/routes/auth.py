from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas.user import UserRegistration, UserResponseOut, LoginRequest, LoginResponse
# import ..models.user as Usermodels
from ..database import get_db
from ..utils.hashing import verify_password, hash_password
from ..core import create_access_token, decode_access_token
from typing import Optional

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserResponseOut)
def register(user: UserRegistration, db: Session = Depends(get_db)):
    """
        Register a new user.
        If user_id exists:
        - if same role exists -> error "already registered"
        - if adding a new role -> verify password matches stored password, then set role flag true
        If user_id does not exist:
        - ensure email not used by another user -> create new user
    """
    existing_user = db.query(User).filter(
        User.user_id == user.user_id).first()

    if existing_user:
        wants_trainer = bool(user.is_trainer)
        wants_participant = bool(user.is_participant)

        existing_user_a_trainer = existing_user.is_trainer
        existing_user_a_participant = existing_user.is_participant

        if (wants_trainer and existing_user_a_trainer) and (wants_participant and existing_user_a_participant):
            raise HTTPException(status_code=status.HTTP_,
                                detail="User already registered with this role.")

        if not verify_password(user.password, existing_user.password):
            raise HTTPException(
                status_code=401, detail="Incorrect password for existing account")

        updated = False
        if wants_trainer and not existing_user_a_trainer:
            existing_user.is_trainer = True
            updated = True

        if wants_participant and not existing_user_a_participant:
            existing_user.is_participant = True
            updated = True

        if updated:
            db.add(existing_user)
            db.commit()
            db.refresh(existing_user)

        else:
            # nothing changed
            raise HTTPException(
                status_code=400, detail="No role changes needed")
    else:
        email_in_use = db.query(User).filter(
            User.email == user.email).first()
        if email_in_use:
            raise HTTPException(
                status_code=400, detail="Email already in use by another account")

        if not (user.is_trainer or user.is_participant):
            raise HTTPException(
                status_code=400, detail="Select at least one role")

        new_user = User(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            password=hash_password(user.password),
            is_trainer=bool(user.is_trainer),
            is_participant=bool(user.is_participant)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return UserResponseOut.model_validate(new_user)


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
        Login: verify user_id and password. Return token + user.
    """
    user = db.query(User).filter(
        User.user_id == credentials.user_id).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=401, detail="Invalid Credentials")

    # Role check
    role = credentials.role.lower()
    if role not in ["trainer", "participant"]:
        raise HTTPException(
            status_code=400, detail="Invalid role")
    if role == "trainer" and not user.is_trainer:
        raise HTTPException(
            status_code=403, detail="User is not registered as trainer")
    if role == "participant" and not user.is_participant:
        raise HTTPException(
            status_code=403, detail="User is not registered as participant")

    role_payload = {
        "is_trainer": user.is_trainer,
        "is_participant": user.is_participant,
        "logged_in_as": role
    }

    access_token = create_access_token(
        sub=str(user.user_id), role_payload=role_payload)

    return LoginResponse(
        user=UserResponseOut.model_validate(user), token=access_token
    )


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Authorization header")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = db.query(User).filter(
        User.user_id == str(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.get("/me", response_model=UserResponseOut)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/all-users", response_model=list[UserResponseOut])
def read_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserResponseOut.model_validate(user) for user in users]
