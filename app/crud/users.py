from datetime import datetime

from app.crud.base import BaseCRUD
from app.models.users import UserBase
from app.schemas.users import User
from app.utils.errors import BaseError, UserNotFoundError


class UsersCRUD(BaseCRUD):
    def get_user(self, user_id: int) -> list[User]:
        if (
            result := self.session.query(UserBase)
            .filter(UserBase.user_id == user_id)
            .one_or_none()
        ):
            return self.wrap_element(
                User,
                result,
            )
        raise UserNotFoundError

    def exists_user(self, user_id: int) -> bool:
        return bool(
            self.session.query(UserBase)
            .filter(UserBase.user_id == user_id)
            .one_or_none()
        )

    def create_user(
        self,
        user_id: str,
        email: str,
        username: str,
        token: str,
        refresh_token: str,
    ) -> list[User]:
        new_user = UserBase(
            user_id=user_id,
            email=email,
            username=username,
            token=token,
            refresh_token=refresh_token,
        )
        self.session.add(new_user)

        try:
            self.session.commit()
            self.session.refresh(new_user)
            return self.wrap_element(User, new_user)
        except Exception as e:
            self.session.rollback()
            raise BaseError(str(e))

    def update_user(
        self,
        user_id: str,
        token: str,
        refresh_token: str,
    ) -> None:
        self.session.query(UserBase).filter(UserBase.user_id == user_id).update(
            {
                UserBase.token: token,
                UserBase.refresh_token: refresh_token,
            },
            synchronize_session="fetch",
        )
        updated_user = (
            self.session.query(UserBase)
            .filter(UserBase.user_id == user_id)
            .one_or_none()
        )

        try:
            self.session.commit()
            return self.wrap_element(User, updated_user)
        except Exception as e:
            self.session.rollback()
            raise BaseError("here" + str(e))
