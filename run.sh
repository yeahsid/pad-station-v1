#!/bin/bash

# Navigate back to the root directory and start the backend and frontend applications with PM2
pm2 start ecosystem.config.js && pm2 save && pm2 startup

# Monitor the status of the applications
pm2 monit
