@echo off

REM Start the backend and frontend applications with PM2
pm2 start ecosystem.config.js && pm2 save

REM Monitor the status of the applications
pm2 monit