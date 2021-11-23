#!/usr/bin/env python

import logging
import os
import time

from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'behave.settings')

    import django
    django.setup()

    from reddit.tasks import process_active_subs

    logger.warning("14: Bot started")

    while True:
        try:
            process_active_subs()
        except OperationalError:
            django.setup()
        except Exception as e:
            logger.warning("15: " + str(e))

        time.sleep(8)


if __name__ == "__main__":
    main()
