pipeline {
    agent any

    stages {

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
                bat 'docker rm -f inventory-container || ver > nul'
                bat 'docker run -d -p 8000:8000 --name inventory-container inventory-api'
            }
        }

     stage('Wait for API') {
    steps {
        powershell 'Start-Sleep -Seconds 10'
    }
}

        stage('Run Tests (Newman)') {
            steps {
                bat 'newman run postman\\inventory_api_tests.postman_collection.json'
            }
        }

        stage('Stop Container') {
             steps {
                bat 'docker stop inventory-container || ver > nul'
                bat 'docker rm inventory-container || ver > nul'
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