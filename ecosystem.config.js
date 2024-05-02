module.exports = {
    apps: [{
        name: "padstation-backend",
        script: "poetry run python run.py",
        interpreter: "bash",
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