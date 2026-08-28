import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from backend.database import engine, Base
from backend.models import *

from backend.database import engine, Base
from backend.models import *

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")