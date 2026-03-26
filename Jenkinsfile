pipeline {
    agent any

    environment {
        ZIP_NAME = "complete-${new Date().format('yyyy-MM-dd-HH-mm-ss')}.zip"
    }

    stages {

        stage('Start') {
            steps {
                echo 'Starting Jenkins pipeline for Inventory API assignment'
            }
        }

        stage('Install Newman') {
            steps {
                bat 'npm install -g newman'
            }
        }

        stage('Install Python Dependencies') {
            steps {
                bat '.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt'
            }
        }

        stage('Run API in Background') {
            steps {
                bat 'start /b .\\.venv\\Scripts\\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000'
                bat 'timeout /t 8'
            }
        }

        stage('Run Newman Tests') {
            steps {
                bat 'newman run .\\postman\\inventory_api_tests.postman_collection.json'
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

        stage('Create Zip Artifact') {
            steps {
                powershell 'Compress-Archive -Path main.py,import_csv_to_mongo.py,requirements.txt,Dockerfile,.dockerignore,Jenkinsfile,README.txt,postman,products.csv -DestinationPath $env:ZIP_NAME -Force'
            }
        }

        stage('Archive Zip') {
            steps {
                archiveArtifacts artifacts: '*.zip', fingerprint: true
            }
        }
    }

    post {
        always {
            bat 'taskkill /F /IM python.exe || exit 0'
            echo 'Pipeline finished. Cleanup attempted.'
        }
    }
}