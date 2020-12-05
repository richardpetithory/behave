#!/usr/bin/env python

import os
import time


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'behave.settings')

    import django
    django.setup()

    from reddit.tasks import process_active_subs

    while True:
        process_active_subs()

        time.sleep(5)


if __name__ == "__main__":
    main()
