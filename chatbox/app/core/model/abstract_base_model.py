from datetime import datetime
from dataclasses import dataclass


@dataclass
class BaseModel:
	id: int
	created: datetime
	modified: datetime
