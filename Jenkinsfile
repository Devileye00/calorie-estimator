pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }
        stage('Test') {
            steps { sh '.venv/bin/python -m pytest -v --junitxml=test-results.xml' }
            post { always { junit 'test-results.xml' } }
        }
    }

    post {
        success { echo 'Pipeline succeeded: all tests passed.' }
        failure { echo 'Pipeline failed. Check the console output.' }
    }
}