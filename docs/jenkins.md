# ci-medic on Jenkins

A full walkthrough of using ci-medic in a Jenkins pipeline.

> **Setup model:** Jenkins has no marketplace that provisions tools into pipelines the way GitHub Actions does. So ci-medic must be present on the agent (a one-time admin step), after which any pipeline can use it with a few lines. A native Jenkins plugin that removes the admin step is on the roadmap.

## What you get

When a build fails, ci-medic reads the captured console log, distills and redacts the secrets, asks a model for a verdict, and writes that verdict to the **build description** which is the editable text at the top of the build page. It updates in place, so it behaves like the GitHub sticky comment but native to Jenkins.

![jenkins ci medic](assets/ci-medic-jenkins.png)

## Step 1 — Admin: make ci-medic available on the agent (one-time)

Pick whichever matches how your agents are provisioned:

**Option A: install on the agent environment:**

```bash
pip install git+https://github.com/alitariq4589/ci-medic
```

**Option B: Docker-based agents:** add the same install line to your agent image so `ci-medic` is on the `PATH` of every build.

Then provide the model key to the agent as an environment variable, or as a Jenkins credential injected into the stage:

```bash
CI_MEDIC_API_KEY="your-key"
```

> ci-medic needs no Jenkins API token and triggers no script-approval prompt. It only reads a log file the pipeline writes. That is deliberate because it stays inside the Groovy sandbox.

## Step 2 — Pipeline author: capture the log and triage on failure

Tee the build output to a file so ci-medic has something to read, then run ci-medic in the `post { failure }` block:

```groovy
pipeline {
  agent any
  stages {
    stage('build') {
      steps {
        sh '''#!/bin/bash
          set -o pipefail
          {
            ./your-build-and-test-commands-here
          } 2>&1 | tee ci-medic-console.log
        '''
      }
    }
  }
  post {
    failure {
      script {
        def verdict = sh(
          script: 'ci-medic jenkins --file ci-medic-console.log --job "$JOB_NAME"',
          returnStdout: true
        ).trim()
        currentBuild.description = verdict
      }
    }
  }
}
```

### Why `set -o pipefail` and the bash shebang matter

Jenkins runs `sh` steps under `/bin/sh` (dash), where a piped command returns the exit code of the **last** command, which always succeeds. That would make a failed build look successful, and the `failure` block would never fire. The `#!/bin/bash` shebang plus `set -o pipefail` makes the pipeline return your command's real exit code, so failures are detected correctly.

![jenkins ci verdict log](assets/jenkins-ci-verdict.png)

## Verifying redaction

The verdict's evidence has secrets redacted before the model ever sees them. To see this yourself, add a line to your test build that prints a dummy AWS key (e.g. the well-known `AKIAIOSFODNN7EXAMPLE` documentation key) and confirm it appears redacted in the build description.

## Roadmap: the native plugin

The setup above is the honest v0.1 path and works on stock Jenkins. The frictionless future; which is: install from the Jenkins Update Center, no agent setup, configure in the UI; requires a real Jenkins plugin, which is planned. Until then, the one-time agent setup is the supported route.