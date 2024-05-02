module.exports = {
    apps: [{
        name: "padstation-backend",
        script: "poetry run gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app",
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