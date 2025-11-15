# data-mining_datahut
Scrapy data extraction assignment.

--EWM Agents Scraper (Scrapy Project)

This project is a Scrapy-based web scraper built to extract real estate agent details from https://www.ewm.com
It collects all agent profiles, cleans the data, and saves the results in JSON, CSV, and SQLite DB formats.


--Project Overview

This spider automatically:

Crawls all agent listing pages
Follows every agent profile URL
Extracts every required field using XPath only
Cleans and structures the data exactly as specified
Saves results in JSON, CSV, and SQLite DB
Stops automatically when all agents are collected (587 total)
Handles pagination, 403 errors, missing fields, etc.

The project follows PEP8 standards, is fully modular, and is organized like a production Scrapy project.
Cleans and structures the data exactly as required

Stores results in:
output/ewm_agents.json
output/ewm_agents.csv
output/ewm_agents.db


--Extracted Fields

Each agent item includes:

profile_url -  Full agent profile link
first_name -  First name
middle_name -  Middle name (may be empty)
last_name -	Last name
address -  Street address
city -  City
state -  State abbreviation
zipcode -  Zipcode
image_url -  Agent profile picture
title -  Job title
website -  Agent website
office_phone_numbers -	List of office phone numbers
agent_phone_numbers -  Direct line / cell number
social -  All available social media links
languages -  List of spoken languages
description -  About/Bio section


--How to Run

Install dependencies:
pip install -r requirements.txt

Run the spider:
scrapy crawl ewm

Output will appear in:
output/

--Data Cleaning & Structuring

The spider ensures:

Duplicate agent profiles are never scraped twice
Empty fields are cleaned (trim spaces, null-handled)
Social links include only available platforms
All fields follow the exact required structure
Address lines are split into city/state/zip properly
Description paragraphs are merged into one clean text

--Technical Features

Custom request headers to avoid 403
Pagination support (Next button crawling)
AutoThrottle enabled
Retry logic for temporary failures
SQLite pipeline for structured storage
Logs important request headers for debugging
Fully PEP8-compliant