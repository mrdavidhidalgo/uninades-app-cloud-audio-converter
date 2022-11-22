#!/bin/sh
gunicorn "app:create_app()" -w 1 -b 0.0.0.0:5000