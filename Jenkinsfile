pipeline {
	agent any
	environment {
		registryCredential = 'dockerhub'
		}

	stages {
		stage('Build') {
			steps {
				sh 'docker build -t aqeel4mpak/blog_site .'
			}
		}
		stage('Test') {
			steps {
				sh 'docker container rm -f blogTest || true'
				sh 'docker container run -p 3000:5000 --name blogTest -d aqeel4mpak/blog_site'
				sh 'sleep 30'
				sh 'curl -I http://localhost:3000'
				sh 'docker container stop blogTest || true'
				sh 'docker container rm -f blogTest || true'
			}
		}
		stage('Publish') {
			steps{
				script {
					docker.withRegistry( '', registryCredential ) {
					sh 'docker push aqeel4mpak/blog_site:latest'
					}
				}
			}
		}
	}
}
