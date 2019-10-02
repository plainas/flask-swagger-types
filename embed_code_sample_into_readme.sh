#!/bin/bash

perl -pe 's/SAMPLE_APP_PLACEHOLDER/`cat sample_app.py`/ge' README.template.md > README.md