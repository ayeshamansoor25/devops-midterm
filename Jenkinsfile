pipeline {
    agent any

    triggers {
        githubPush()          // GitHub webhook starts this job on every push
    }

    options {
        disableConcurrentBuilds()
    }

    environment {
        IMAGE         = 'midterm-app'
        CONTAINER     = 'midterm-app'
        TEACHER_EMAIL = 'qasimalik@gmail.com'
    }

    stages {
        stage('Fetch latest data') {
            steps {
                checkout scm
                sh 'git log -1 --oneline && wc -l dataset/train.csv'
                script {
                    env.STUDENT_ID = sh(returnStdout: true,
                        script: "python3 -c 'import json; print(json.load(open(\"config.json\"))[\"student_id\"])'").trim()
                    env.GIT_SHA = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
                }
                echo "Student: ${env.STUDENT_ID}  Commit: ${env.GIT_SHA}"
            }
        }

        stage('Build base image') {
            steps {
                sh 'docker build --target base -t ${IMAGE}-base .'
            }
        }

        stage('Train model') {
            steps {
                sh '''
                    docker run --rm --user $(id -u):$(id -g) -e HOME=/tmp \
                        -e GIT_COMMIT=${GIT_SHA} \
                        -v "$WORKSPACE":/app -w /app ${IMAGE}-base python train.py
                '''
            }
        }

        stage('Run tests') {
            steps {
                sh '''
                    docker run --rm --user $(id -u):$(id -g) -e HOME=/tmp \
                        -v "$WORKSPACE":/app -w /app ${IMAGE}-base \
                        python -m pytest -q -p no:cacheprovider tests
                '''
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build --target app -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest .'
            }
        }

        stage('Deploy on EC2') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER} || true
                    docker run -d --name ${CONTAINER} --restart unless-stopped \
                        -p 8000:8000 ${IMAGE}:latest
                    for i in $(seq 1 30); do
                        if curl -sf http://localhost:8000/metrics; then echo; echo "Deployed OK"; exit 0; fi
                        sleep 2
                    done
                    echo "App did not start"; docker logs ${CONTAINER}; exit 1
                '''
                sh 'docker image prune -f || true'
            }
        }
    }

    post {
        always {
            script {
                def metrics = fileExists('artifacts/metrics.json') ? readFile('artifacts/metrics.json') : 'metrics not available'
                emailext(
                    to: env.TEACHER_EMAIL,
                    subject: "${env.STUDENT_ID} - MIDTERM model retrained - Build #${env.BUILD_NUMBER} ${currentBuild.currentResult}",
                    body: """Student Reg No: ${env.STUDENT_ID}
Build result: ${currentBuild.currentResult}
Job: ${env.JOB_NAME} #${env.BUILD_NUMBER}
Commit: ${env.GIT_SHA}

New model metrics:
${metrics}

Build log: ${env.BUILD_URL}
""",
                    mimeType: 'text/plain'
                )
            }
        }
    }
}
