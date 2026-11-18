pipeline {
    agent any

    environment {
        APP_CONTAINER = "flask-vuln-app"
        APP_IMAGE = "flask-vuln-image:latest"
    }

    stages {
        stage('Build') {
            steps {
                echo '--- ETAPA 1: BUILD (Construyendo imagen Docker de la app) ---'
                sh 'docker build -t ${APP_IMAGE} .'
            }
        }
        stage('Test') {
            steps {
                echo '--- ETAPA 2: TEST (Ejecutando pruebas unitarias) ---'
                sh 'docker run --rm ${APP_IMAGE} python test_app.py'
            }
        }
        stage('Analyze') {
            steps {
                echo '--- ETAPA 3: ANALYZE (Analisis SAST con SonarQube) ---'
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=devsecops-flask-vuln \
                            -Dsonar.projectName="DevSecOps Flask Vulnerable" \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3.9
                        """
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                echo '--- ETAPA 4: DEPLOY (Desplegando app en entorno de prueba para ZAP) ---'
                sh 'docker rm -f ${APP_CONTAINER} || true'
                sh 'docker run -d --name ${APP_CONTAINER} --network devsecops-net -p 5000:5000 ${APP_IMAGE}'
                sh 'sleep 5'
            }
        }
        stage('Security Test') {
            steps {
                echo '--- ETAPA 5: SECURITY TEST (OWASP Dependency-Check y OWASP ZAP) ---'
                sh 'mkdir -p odc-reports zap-reports && chmod 777 odc-reports zap-reports'
                catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
                    dependencyCheck additionalArguments: '--scan ./requirements.txt --enableExperimental --noupdate --format HTML --format XML --out ./odc-reports', odcInstallation: 'DP-Check'
                }
                sh '''
                    docker volume rm zap_wrk_vol || true
                    docker volume create zap_wrk_vol
                    docker run --rm -u 0 --network devsecops-net \
                      -v zap_wrk_vol:/zap/wrk \
                      ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                      -t http://flask-vuln-app:5000/hello?name=TEST \
                      -r zap_report.html || true
                    docker run --rm -v zap_wrk_vol:/zap/wrk busybox cat /zap/wrk/zap_report.html > ./zap-reports/zap_report.html
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'odc-reports/*, zap-reports/*', allowEmptyArchive: true
        }
    }
}
