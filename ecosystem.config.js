module.exports = {
    apps: [{
        name: "padstation-backend",
        script: "run.py",
        args: "poetry run python run.py",
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