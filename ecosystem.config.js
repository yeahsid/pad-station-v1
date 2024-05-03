module.exports = {
    apps: [{
        name: "padstation-backend",
        cwd: "./backend",
        script: "poetry run gunicorn -w 1 -k uvicorn.workers.UvicornWorker  app.main:app -b 0.0.0.0:8000 ",
        env: {
            NODE_ENV: "production",
        },
        watch: false,
        restart_delay: 3000
    },
    {
        name: "padstation-frontend",
        script: "npm run prod",
        cwd: "./frontend",
        env: {
            NODE_ENV: "production",
        },
        watch: false,
        restart_delay: 3000
    }]
}