pipeline {
    agent any

    stages {

        stage('Install Newman') {
            steps {
                bat '"C:\\Program Files\\nodejs\\npm.cmd" install newman --no-save'
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
                bat 'docker run -d -p 8000:8000 --name inventory-container --env-file .env.jenkins inventory-api'
            }
        }

        stage('Wait for API') {
            steps {
                powershell 'Start-Sleep -Seconds 10'
            }
        }

        stage('Run Tests (Newman)') {
            steps {
                bat '.\\node_modules\\.bin\\newman.cmd run postman\\inventory_api_tests.postman_collection.json'
            }
        }

        stage('Generate README') {
            steps {
                bat '''
                (
                echo Inventory Management API Endpoints
                echo.
                echo /getSingleProduct?product_id=INTEGER
                echo /getAll
                echo /addNew  ^(POST JSON body: ProductID, Name, UnitPrice, StockQuantity, Description^)
                echo /deleteOne?product_id=INTEGER
                echo /startsWith?letter=CHARACTER
                echo /paginate?start_id=INTEGER^&end_id=INTEGER
                echo /convert?product_id=INTEGER
                echo.
                echo FastAPI interactive docs available at /docs
                ) > README.txt
                '''
            }
        }

        stage('Create ZIP') {
            steps {
                powershell '$ts = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"; Compress-Archive -Path main.py,import_csv_to_mongo.py,requirements.txt,Dockerfile,.dockerignore,Jenkinsfile,README.txt,postman,products.csv,.env.jenkins -DestinationPath ("complete-" + $ts + ".zip") -Force'
            }
        }

        stage('Archive ZIP') {
            steps {
                archiveArtifacts artifacts: 'complete-*.zip', fingerprint: true
            }
        }
    }

    post {
        always {
            bat 'docker stop inventory-container || ver > nul'
            bat 'docker rm inventory-container || ver > nul'
            bat 'taskkill /F /IM python.exe || ver > nul'
            echo 'Pipeline finished. Cleanup attempted.'
        }
    }
}