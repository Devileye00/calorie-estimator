pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\Vishwajeet Shinde\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m venv .venv'
                bat '.venv\\Scripts\\python -m pip install --upgrade pip'
                bat '.venv\\Scripts\\python -m pip install -r requirements.txt'
            }
        }
        stage('Test') {
            steps { bat '.venv\\Scripts\\python -m pytest -v --junitxml=test-results.xml' }
            post { always { junit allowEmptyResults: true, testResults: 'test-results.xml' } }
        }
    }

    post {
        success { echo 'Pipeline succeeded: all tests passed.' }
        failure { echo 'Pipeline failed. Check the console output.' }
    }
}