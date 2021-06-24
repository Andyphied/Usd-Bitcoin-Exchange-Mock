import logging

from fastapi import APIRouter

from database.data import in_memory_datastore
from .endpoints import users_router, coin_router

logger = logging.getLogger(__name__)

router = APIRouter()
router.include_router(coin_router, tags=["bitcoin_rate"])
router.include_router(users_router, tags=["user"])


@router.on_event("shutdown")
def shutdown_event():
    logger.info("Shutdown sequence initaited")
    in_memory_datastore = {}
    logger.info("Shutdown sequence complete")
