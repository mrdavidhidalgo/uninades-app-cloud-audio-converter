#!/bin/sh
gunicorn "app:create_app()" -w 3 -b 0.0.0.0:5000