# Stop and delete all PM2 processes
pm2 stop all
pm2 delete all

# Navigate to the frontend directory and build the project
cd frontend
npm run build

# Navigate back to the root directory
cd ..

# Start PM2 processes using the ecosystem configuration
pm2 start ecosystem.config.js

# Open the PM2 dashboard
pm2 dashboard