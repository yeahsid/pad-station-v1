#!/bin/bash

# Navigate back to the root directory and start the backend and frontend applications with PM2
npx pm2 start ecosystem.config.js && npx pm2 save

# Monitor the status of the applications
npx pm2 monit
