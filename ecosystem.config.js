const path = require('path');

module.exports = {
  apps: [
    {
      name: 'backend',
      script: process.platform === 'win32' ? 'backend\\main.py' : 'backend/main.py',
      interpreter: process.platform === 'win32' 
        ? path.join(__dirname, 'backend', '.venv', 'Scripts', 'python.exe') 
        : path.join(__dirname, 'backend', '.venv', 'bin', 'python'),
      cwd: path.join(__dirname, 'backend'),
      watch: true,
      env: {
        PYTHON_ENV: 'development'
      },
      log_file: path.join(__dirname, 'logs', 'backend.log'),
      error_file: path.join(__dirname, 'logs', 'backend-error.log'),
      out_file: path.join(__dirname, 'logs', 'backend-out.log')
    },
    {
      name: 'frontend',
      script: 'npm',
      args: 'start',
      interpreter: 'node',
      exec_mode: 'fork',
      cwd: path.join(__dirname, 'frontend'),
      watch: true,
      env: {
        NODE_ENV: 'development'
      },
      log_file: path.join(__dirname, 'logs', 'frontend.log'),
      error_file: path.join(__dirname, 'logs', 'frontend-error.log'),
      out_file: path.join(__dirname, 'logs', 'frontend-out.log')
    }
  ]
};
