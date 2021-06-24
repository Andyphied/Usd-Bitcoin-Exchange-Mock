import logging

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic.networks import EmailStr

from database.data import in_memory_datastore
from schema.users import UserIn, UserInDb, UserUpdate

logger = logging.getLogger(__name__)


class CRUDUser:
    def __init__(self, model: UserInDb) -> None:
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model (UserInDb): A Pony Entity class
        """
        self.model = model

    def get(self, *, id: Any) -> Optional[UserInDb]:
        """Get data from database using the uuid

        Args:
            id (Any): the primarykey/identifier

        Returns:
            Optional[UserInDb]: The Entity Object ( Pony Entity Class)
        """
        logger.info(f"Acessing db to get {id}")
        obj = in_memory_datastore["users"]

        obj = in_memory_datastore["users"].get(id)
        logger.info(f"Done transacting with db")
        return obj

    def get_by_email(self, *, email: EmailStr) -> Optional[UserInDb]:

        logger.info(f"Attempting to retrieve user by email")
        objs = in_memory_datastore["users"]

        fields = objs.values()
        if len(fields) == 0:
            logger.info("No objects in database")
            return None

        for field in fields:
            if objs[field].email == email:
                logger.error(f"User with email: {email} found")
                return objs[field]

        logger.error(f"User with email: {email} not found")
        return None

    def get_by_username(self, *, username: str):

        logger.info(f"Attempting to retrieve user by username")
        objs = in_memory_datastore["users"]

        fields = objs.keys()
        if len(fields) == 0:
            logger.info("No objects in database")
            return None
        for field in fields:
            if objs[field].username == username:
                logger.error(f"User with email: {username} found")
                return objs[field]
        return None

    def create(self, *, obj_in: Union[UserIn, Dict[str, Any]]) -> UserInDb:
        """Create or Store new data

        Args:
            obj_in (Union[CreateSchema, Dict[str, Any]]): the data to store

        Returns:
            UserInDb: [description]
        """

        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = jsonable_encoder(obj_in)

        _id = uuid4()

        obj_in_data["id"] = str(_id)
        obj_in_data["createdAt"] = datetime.now()

        db_obj = UserInDb(**obj_in_data)

        logger.info("Inserting user details into database")
        in_memory_datastore["users"][str(_id)] = db_obj
        logger.info("User sucessfully inserted into database")

        return db_obj

    def update(self, *, db_obj: UserInDb,
               obj_in: Union[UserUpdate, Dict[str, Any]]) -> UserInDb:
        """Heps handle update of entities data

        Args:
            db_obj (UserInDb): The ddb obju
            obj_in (Union[UpdateSchema, Dict[str, Any]]): the update data

        Returns:
            UserInDb: [description]
        """

        db_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        update_data["updatedAt"] = datetime.now()
        for field in db_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        logger.info("Performing user details update")
        in_memory_datastore["users"][db_obj.id] = db_obj

        return db_obj

    def deposit(self, *, id: Any, amount: float) -> UserInDb:
        """Deposit amount for user

        Args:
            id (Any): The user id
            amount (float): The amount

        Returns:
            UserInDb: the db object
        """
        logger.info("Acesssing database")
        obj = self.get(id=id)

        obj.usdBalance += amount
        obj.updatedAt = datetime.now()

        in_memory_datastore["users"]["id"] = obj
        logger.info(f"User: {id} amount deposited and db updated")

        return {"successful": True, "data": obj}

    def withdrawal(
            self, *, id: Any,
            amount: float) -> Union[UserInDb, Dict[str, Union[bool, str]]]:
        """Withdrwal amount for user

        Args:
            id (Any): The user id
            amount (float): The amount

        Returns:
            Union[UserInDb, Dict[str, Union[bool, str]]]: User Object ot Error Dict
        """
        logger.info("Acesssing database")
        obj = self.get(id=id)
        if amount > obj.usdBalance:
            logger.error(f"User: {id} has insufficent balance")
            return {"successful": False, "msg": "Insuffcient Usd Balance"}

        obj.usdBalance -= amount
        obj.updatedAt = datetime.now()

        in_memory_datastore["users"]["id"] = obj

        logger.info(f"User: {id} amount withdrawed and db updated")
        return {"successful": True, "data": obj}

    def coin_conversion(self, amount: float, _type: int) -> float:
        """Convert coin to cash ot cash to coin

        Args:
            amount (float): coin amount or cash amount
            _type (int): 0 -> cash to coin
                        1 -> coint to cash

        Returns:
            [float]: amount of coin or cash
        """
        if _type == 1:
            rate = in_memory_datastore["bitcoin_rate"].price
            value = amount * rate
        elif _type == 0:
            rate = in_memory_datastore["bitcoin_rate"].price
            value = amount / rate
        logger.info(f"User: {id} acessed coin conversion function")
        return value

    def buy(self, *, id: Any,
            amount: float) -> Union[UserInDb, Dict[str, Union[bool, str]]]:
        """Buy Bitcoin

        Args:
            id (Any): user_id
            amount (float): the usd amount available

        Returns:
            Union[UserInDb, Dict[str, Union[bool, str]]]: User Object ot Error Dict
        """
        logger.info("Acesssing database")
        obj = self.get(id=id)

        coin_value = self.coin_conversion(amount, _type=1)

        if coin_value > obj.usdBalance:
            logger.error(f"User: {id} has insufficent balance")
            return {"successful": False, "msg": "Insuffcient Usd Balance"}

        obj.usdBalance -= coin_value
        obj.bitcoinAmount += amount
        obj.updatedAt = datetime.now()

        in_memory_datastore["users"]["id"] = obj
        logger.info(f"User: {id} bought coins and db updated ")

        return {"successful": True, "data": obj}

    def sell(self, *, id: Any,
             amount: float) -> Union[UserInDb, Dict[str, Union[bool, str]]]:
        """Sell Bitcoin

        Args:
            id (Any): user_id
            amount (float): the usd amount available

        Returns:
           Union[UserInDb, Dict[str, Union[bool, str]]]: User Object ot Error Dict
        """
        logger.info("Acesssing database")
        obj = self.get(id=id)

        if amount > obj.bitcoinAmount:
            return {"successful": False, "msg": "Insuffcient Bitcoin Balance"}

        cash = self.coin_conversion(amount=amount, _type=1)

        obj.usdBalance += cash
        obj.bitcoinAmount -= amount
        obj.updatedAt = datetime.now()

        in_memory_datastore["users"]["id"] = obj
        logger.info(f"User: {id} sold coins and db updated")

        return {"successful": True, "data": obj}

    def get_balance(self, *, id: Any) -> float:
        """Get User Balance

        Args:
            id (Any): user id

        Returns:
            float: user balanace in usd
        """
        logger.info("Acesssing database")
        obj = self.get(id=id)

        usd_amount = obj.usdBalance
        usd_amount += self.coin_conversion(amount=obj.bitcoinAmount, _type=1)

        logger.info("User balance grabbed")
        return usd_amount


user_crud = CRUDUser(UserInDb)