#!/bin/bash

( sleep 1 && xdg-open "http://localhost:8000" ) &
python3 main.py
