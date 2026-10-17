# Jenkins with Python and Ansible installed
FROM jenkins/jenkins:lts-jdk21
USER root
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv ansible \
    && rm -rf /var/lib/apt/lists/*
USER jenkins
