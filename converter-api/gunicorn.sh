#!/bin/sh
gunicorn "app:create_app()" -w 4 --threads 4 -b 0.0.0.0:5000