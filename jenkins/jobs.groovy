pipelineJob('JG-Repuestos') {
    description('Entrega 2: pruebas, construccion y prueba de humo desde GitHub.')
    parameters {
        stringParam('BRANCH', 'master', 'Rama publicada que contiene el Jenkinsfile.')
    }
    definition {
        cpsScm {
            scm {
                git {
                    remote {
                        url(System.getenv('JG_REPOSITORY_URL'))
                        if (System.getenv('JG_GITHUB_TOKEN')) {
                            credentials('jg-github')
                        }
                    }
                    branch('${BRANCH}')
                }
            }
            scriptPath('Jenkinsfile')
            lightweight(false)
        }
    }
}
