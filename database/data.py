from datetime import datetime
from typing import Any, Dict, Union

from schema import UserInDb, BitcoinIn

init_data = {"price": 100.00, "updatedAt": datetime.now()}

bitcoin_price = BitcoinIn(**init_data)

in_memory_datastore: Dict[str, Union[Dict[str, UserInDb],
                                     Dict[str, BitcoinIn]]] = {
                                         "bitcoin_rate": bitcoin_price,
                                         "users": {}
                                     }
