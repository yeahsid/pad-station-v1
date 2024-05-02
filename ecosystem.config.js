module.exports = {
    apps : [{
      name: "padstation-backend",
      script: "run.py",
      interpreter: "python3",
      env: {
        NODE_ENV: "production",
      },
      watch: true,
      ignore_watch : ["node_modules", "logs", ".git"],
      watch_options: {
        "followSymlinks": false
      },
      restart_delay: 3000
    },
    {
      name: "padstation-frontend",
      script: "npm",
      args: "run prod",
      interpreter: "none",
      cwd: "./frontend",
      env: {
        NODE_ENV: "production",
      },
      watch: true,
      ignore_watch : ["node_modules", "logs", ".git"],
      watch_options: {
        "followSymlinks": false
      },
      restart_delay: 3000
    }]
  }