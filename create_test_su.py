import logging

from django.contrib.auth import get_user_model
from django.db import IntegrityError

log = logging.getLogger("Create Test Super User")
logging.basicConfig(
    level=logging.DEBUG
)

try:
    User = get_user_model()
    User.objects.create_superuser("resman", 'resman@resman.com', "resman_password")
except IntegrityError as ex:
    log.info("Test user already existed.")
except Exception as ex:
    log.error("Error while creating test super user", exc_info=ex)
