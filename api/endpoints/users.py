import logging
from fastapi import APIRouter, HTTPException, status

from core.config import settings
from crud import user_crud

from schema import UserIn, UserOut, UserUpdate, UserUsdTransaction, UserBitcoinTransaction, UserBalance

router = APIRouter(prefix="/users")
logger = logging.getLogger(__name__)


def check_figures(price, bitcoin: bool = False):
    if price < 0:
        data = {"status": "error", "msg": "invalid amount"}
        if bitcoin:
            logger.error("Negative bitcoin amount passed in")
        else:
            logger.error("Negative amount(usd) passed in")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=data)
    if price == 0:
        data = {"status": "error", "msg": "invalid amount"}
        if bitcoin:
            logger.error("Invalid amount passed in")
        else:
            logger.error("Invalid amount passed in")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=data)
    if bitcoin:
        if price > settings.BITCOIN_LIMIT:
            data = {
                "status": "error",
                "msg": "user can not buy or sell more than 100 bitcoins"
            }
            logger.error(
                "User attempted to buy or sell bitcoin amount above limit")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=data)
    else:
        if price > settings.USD_LIMIT:
            data = {
                "status": "error",
                "msg": "can not deposit or withdraw such figures "
            }
            logger.error(
                "User attempted to withdraw or depoist amount (usd) above limit"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=data)
    return price


@router.post("/", response_model=UserOut, status_code=201)
async def create_user(user: UserIn):

    logger.info("User creation initialized")

    if user_crud.get_by_username(username=user.username):
        data = {"status": "error", "msg": "user with username exists"}
        logger.error("User with username exists")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=data)

    if user_crud.get_by_email(email=user.email):
        data = {"status": "error", "msg": "user with email exists"}
        logger.error("User with email exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=data)

    data_obj = user_crud.create(obj_in=user)
    logger.info(f"User: {data_obj.id} sucessfully created ")

    data = data_obj.dict()
    return data


@router.get("/{id}", response_model=UserOut)
async def get_user(id: str):

    logger.info(f"attempting to get user with id: {id}")

    data_obj = user_crud.get(id=id)

    if not data_obj:
        data = {"status": "error", "msg": "user with id does not exists"}
        logger.error("User with this id doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data)

    logger.info(f"User: {id} retrieved successfully")

    data = data_obj.dict()
    return data


@router.put("/{id}", response_model=UserOut)
async def update_user(id: str, update_obj: UserUpdate):

    logger.info(f"attempting to updated user with id: {id}")

    data_obj = user_crud.get(id=id)
    if not data_obj:
        data = {"status": "error", "msg": "user with id does not exists"}
        logger.error("User with this id doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data)

    updated_obj = user_crud.update(db_obj=data_obj, obj_in=update_obj)

    logger.info(f" User: {id} updated sucessfully")
    data = updated_obj.dict()
    return data


@router.post("/{id}/usd", response_model=UserOut)
async def usd_balance(id: str, user_trans: UserUsdTransaction):
    logger.info(f"User: {id} usd transaction initialized")

    data_obj = user_crud.get(id=id)
    if not data_obj:
        data = {"status": "error", "msg": "user with id does not exists"}
        logger.error("User with this id doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data)

    check_figures(price=user_trans.amount)

    if user_trans.action.value == "deposit":
        logger.info(f"User: {id} performing a deposit transaction")
        user_obj = user_crud.deposit(id=id, amount=user_trans.amount)

    elif user_trans.action.value == "withdraw":
        logger.info(f"User: {id} performing a withdrawal transaction")
        user_obj = user_crud.withdrawal(id=id, amount=user_trans.amount)
        if not user_obj["successful"]:
            data = {"status": "error", "msg": user_obj["msg"]}
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=data)

    else:
        data = {"status": "error", "msg": "invalid action"}
        logger.error(f"User: {id} tried unknown action")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=data)
    logger.info(f"User: {id} {user_trans.action} performmed sucessfully")

    data = user_obj["data"].dict()
    return data


@router.post("/{id}/bitcoins", response_model=UserOut)
async def bitcoin_balance(id: str, user_trans: UserBitcoinTransaction):
    logger.info(f"User: {id} bitcoin transaction initialized")

    data_obj = user_crud.get(id=id)
    if not data_obj:
        data = {"status": "error", "msg": "user with id does not exists"}
        logger.error("User with this id doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data)

    check_figures(price=user_trans.amount, bitcoin=True)

    if user_trans.action.value == "buy":
        logger.info(f"User: {id} buying bitcoin")
        user_obj = user_crud.buy(id=id, amount=user_trans.amount)
        if not user_obj["successful"]:
            data = {"status": "error", "msg": user_obj["msg"]}
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=data)

    elif user_trans.action.value == "sell":
        logger.info(f"User: {id} selling bitcoin")
        user_obj = user_crud.sell(id=id, amount=user_trans.amount)
        if not user_obj["successful"]:
            data = {"status": "error", "msg": user_obj["msg"]}
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=data)
    else:
        data = {"status": "error", "msg": "invalid action"}
        logger.error(f"User: {id} attempted unknown action")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=data)

    logger.info(f"User: {id} {user_trans.action} performmed sucessfully")

    data = user_obj["data"].dict()
    return data


@router.get("/{id}/balance", response_model=UserBalance)
async def usd_balance(id: str):
    logger.info(f"User: {id} balance retrieval initialized")

    data_obj = user_crud.get(id=id)
    if not data_obj:
        data = {"status": "error", "msg": "user with id does not exists"}
        logger.error("User with this id doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data)

    user_obj = user_crud.get_balance(id=id)

    data = {"total_balance": user_obj}
    logger.info(f"User: {id} retrieved user balance")

    return data
