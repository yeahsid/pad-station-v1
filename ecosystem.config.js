module.exports = {
    apps: [{
        name: "my-app",
        script: "run.py",
        interpreter: "python3",
        env: {
            NODE_ENV: "development",
        },
        env_production: {
            NODE_ENV: "production",
        }
    },
    {
        name: "my-frontend",
        script: "npm",
        args: "run start",
        interpreter: "none",
        cwd: "./frontend",
        env: {
            NODE_ENV: "development",
        },
        env_production: {
            NODE_ENV: "production",
        }
    }]
}