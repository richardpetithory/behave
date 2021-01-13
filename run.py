#!/usr/bin/env python

import logging
import os
import time

logger = logging.getLogger(__name__)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'behave.settings')

    import django
    django.setup()

    from reddit.tasks import process_active_subs

    logger.warning("Bot started")

    while True:
        try:
            process_active_subs()
        except Exception as e:
            logger.warning(e)

        time.sleep(8)


if __name__ == "__main__":
    main()
