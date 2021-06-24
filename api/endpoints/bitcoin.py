import logging

from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from database.data import in_memory_datastore
from schema import BitcoinIn

router = APIRouter(prefix="/bitcoin")

logger = logging.getLogger(__name__)


def get_bitcoin_rate() -> BitcoinIn:
    obj = in_memory_datastore.get("bitcoin_rate")

    if not obj:
        data = {"status": "error", "msg": "bitcoin rate not found"}
        logger.error(msg="Bitcoin rate not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=data)
    return obj


@router.put("/", response_model=BitcoinIn)
async def update_bitcoin_rate(obj: BitcoinIn,
                              rate_obj: BitcoinIn = Depends(get_bitcoin_rate)):

    logger.info(msg="Recived request to update bitcoin rate")

    price = obj.price

    if price <= 0:
        data = {"status": "error", "msg": "invalid bitcoin rate"}
        logger.info(msg="Invalid bitcoin rate recieved (negative)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=data)
    if price > 999999:
        data = {
            "status": "error",
            "msg": "invalid bitcoin rate at this moment"
        }
        logger.info(msg="Invalid bitcoin rate recieved (Huge)")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=data)

    rate_obj.price = price
    rate_obj.updatedAt = datetime.now()

    in_memory_datastore["bitcoin_rate"] = rate_obj

    logger.info(msg="Bitcoin rate updated successfully")

    return rate_obj


@router.get("/", response_model=BitcoinIn)
async def get_bitcoin_rate(rate_obj: Dict[str,
                                          Any] = Depends(get_bitcoin_rate)):
    logger.info(msg="Recived request to get bitcoin rate")
    return rate_obj