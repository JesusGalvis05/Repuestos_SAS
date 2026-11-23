FROM docker:29.9.2-cli AS docker-cli
FROM jenkins/jenkins:2.580.2-jdk21

USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker-cli /usr/local/libexec/docker/cli-plugins/ /usr/local/libexec/docker/cli-plugins/
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
USER jenkins
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt --latest=false
COPY casc.yaml /usr/share/jenkins/ref/casc.yaml
COPY jobs.groovy /usr/share/jenkins/ref/jobs.groovy
