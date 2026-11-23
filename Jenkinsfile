pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '15', artifactNumToKeepStr: '10'))
    }
    environment {
        CI_RUN_ID = "jenkins-${BUILD_NUMBER}"
    }
    stages {
        stage('Pruebas automatizadas') {
            steps {
                deleteDir()
                checkout scm
                sh 'python3 scripts/ci_pipeline.py test'
            }
            post {
                always {
                    junit testResults: 'ci-results/**/pytest.xml', allowEmptyResults: true
                }
            }
        }
        stage('Construccion de imagen') {
            steps {
                sh 'python3 scripts/ci_pipeline.py build'
            }
        }
        stage('Prueba de humo') {
            steps {
                sh 'python3 scripts/ci_pipeline.py smoke'
            }
        }
    }
    post {
        always {
            script {
                try {
                    sh 'python3 scripts/ci_pipeline.py cleanup'
                } finally {
                    archiveArtifacts artifacts: 'ci-results/**/*', allowEmptyArchive: true
                }
            }
        }
    }
}
