pipeline {
    agent any

    stages {

        stage('Clone Repo') {
            steps {
                git 'https://github.com/ibrah113/web-services-assignment1.git'
            }
        }

        stage('Install Newman') {
            steps {
                bat '"C:\\Program Files\\nodejs\\npm.cmd" install -g newman'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t inventory-api .'
            }
        }

        stage('Run Container') {
            steps {
                bat 'docker run -d -p 8000:8000 --name inventory-container inventory-api'
            }
        }

        stage('Wait for API') {
            steps {
                bat 'timeout /t 10'
            }
        }

        stage('Run Tests (Newman)') {
            steps {
                bat 'newman run postman\\inventory_api_tests.postman_collection.json'
            }
        }

        stage('Stop Container') {
            steps {
                bat 'docker stop inventory-container'
                bat 'docker rm inventory-container'
            }
        }

        stage('Create ZIP') {
            steps {
                bat 'powershell Compress-Archive -Path * -DestinationPath complete.zip -Force'
            }
        }
    }

    post {
        always {
            bat 'taskkill /F /IM python.exe || ver > nul'
            echo 'Pipeline finished. Cleanup attempted.'
        }
    }
}