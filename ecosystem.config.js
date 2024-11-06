const path = require('path');

module.exports = {
  apps: [
    {
      name: 'backend',
      script: 'uvicorn',
      args: 'backend.main:app --reload --host 0.0.0.0 --port 8000',
      interpreter: path.join(__dirname, 'backend', '.venv', 'bin', 'python'),
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
