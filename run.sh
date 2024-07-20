#!/bin/bash

# Navigate back to the root directory and start the backend and frontend applications with PM2
pm2 delete all
pm2 start ecosystem.config.js && pm2 save && pm2 startup

# sudo env PATH=$PATH:~/.nvm/versions/node/v22.1.0/bin ~/.nvm/versions/node/v22.1.0/lib/node_modules/pm2/bin/pm2 startup systemd -u padstation --hp ~/


# Monitor the status of the applications
pm2 monit
