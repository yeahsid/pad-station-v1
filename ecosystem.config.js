module.exports = {
    apps: [{
        name: "padstation-backend",
        cwd: "./backend",
        script: "poetry run fastapi run app/main.py",
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