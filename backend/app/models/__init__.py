from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .document import Document
from .collection import Collection
from .conversation import Conversation