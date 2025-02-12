#!/bin/bash

uvicorn mybenchproyect.asgi:application --host 0.0.0.0 --port 8000 --reload --workers 1
