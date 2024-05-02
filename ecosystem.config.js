module.exports = {
    apps: [{
        name: "padstation-backend",
        script: "gunicorn",
        args: "-w 4 -k uvicorn.workers.UvicornWorker app.main:app",
        interpreter: "none",
        env: {
            NODE_ENV: "production",
        },
        watch: false,
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
        watch: false,
        restart_delay: 3000
    }]
}