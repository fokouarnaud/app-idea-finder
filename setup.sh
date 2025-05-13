#!/bin/bash

# Installation forcée de google-play-scraper
pip install --upgrade pip
pip install google-play-scraper==1.2.4 --force-reinstall

# Afficher les packages installés pour le débogage
pip list | grep google-play-scraper
