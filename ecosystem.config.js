module.exports = {
    apps: [{
        name: "padstation-backend",
        script: "run.py",
        interpreter: "python3",
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