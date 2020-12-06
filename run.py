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
        process_active_subs()

        time.sleep(5)


if __name__ == "__main__":
    main()
