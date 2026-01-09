#!/bin/bash

# Set UTF-8 encoding for Korean filenames
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export LANGUAGE=C.UTF-8

# Clean previous build
rm -rf _site .jekyll-cache

# Build Jekyll
bundle exec jekyll build
