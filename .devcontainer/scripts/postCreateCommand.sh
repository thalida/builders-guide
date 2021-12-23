#!/bin/bash

cd /workspaces/builders-guide/api
pipenv install --dev

cd /workspaces/builders-guide/app
npm install
