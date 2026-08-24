# CI Platforms

What it shows: the same carbon budget gate on the sixteen CI/CD systems that
aren't GitHub Actions. One file per platform, each one a drop-in.

The action wrapper is GitHub-specific; the estimator is not. `carbon_budget.py`
is stdlib-only Python 3.10+ that reads its inputs from environment variables and
exits `1` when the estimate is over budget. That is the entire contract, and
every file here is the same four lines dressed in a different syntax:

```sh
curl -fsSL -o carbon_budget.py \
  https://raw.githubusercontent.com/fabiocicerchia/carbon-budget-action/v0.2.0/carbon_budget.py
BUDGET_GCO2E=5000 REPLICAS=4 CPU_REQUEST=500m MEMORY_REQUEST=1Gi \
  GRID_INTENSITY=56 python3 carbon_budget.py
```

Pin the tag (`v0.2.0` above), not `main` — a gate that changes underneath you
fails builds you didn't change.

## Files

| Platform | File | Copy it to |
|---|---|---|
| GitLab CI | [`gitlab-ci.yml`](gitlab-ci.yml) | `.gitlab-ci.yml` |
| CircleCI | [`circleci-config.yml`](circleci-config.yml) | `.circleci/config.yml` |
| Travis CI | [`travis.yml`](travis.yml) | `.travis.yml` |
| Azure DevOps | [`azure-pipelines.yml`](azure-pipelines.yml) | `azure-pipelines.yml` |
| AWS CodePipeline | [`buildspec.yml`](buildspec.yml) | `buildspec.yml` (CodeBuild stage) |
| Devtron | [`devtron-task.sh`](devtron-task.sh) | a Pre-Deployment custom-script task |
| Northflank | [`northflank-job.json`](northflank-job.json) | `northflank create job manual -f …` |
| Spacelift | [`spacelift-config.yml`](spacelift-config.yml) | `.spacelift/config.yml` |
| Jenkins | [`Jenkinsfile`](Jenkinsfile) | `Jenkinsfile` |
| Bitbucket Pipelines | [`bitbucket-pipelines.yml`](bitbucket-pipelines.yml) | `bitbucket-pipelines.yml` |
| Google Cloud Build | [`cloudbuild.yaml`](cloudbuild.yaml) | `cloudbuild.yaml` |
| Tekton | [`tekton.yaml`](tekton.yaml) | `kubectl apply -f` |
| Argo Workflows | [`argo-workflow.yaml`](argo-workflow.yaml) | `argo submit` |
| Harness | [`harness-pipeline.yml`](harness-pipeline.yml) | the pipeline's YAML editor |
| Buildkite | [`buildkite-pipeline.yml`](buildkite-pipeline.yml) | `.buildkite/pipeline.yml` |
| Drone / Woodpecker | [`drone.yml`](drone.yml) | `.drone.yml` / `.woodpecker.yml` |

For GitHub Actions use the action itself — see [`../basic/`](../basic/) and
[`../error-budget/`](../error-budget/).

## Inputs

Every action input has an environment variable behind it. The mapping is
mechanical: upper-case, dashes to underscores. `budget-gco2e` → `BUDGET_GCO2E`,
`grid-intensity` → `GRID_INTENSITY`, `manifest-path` → `MANIFEST_PATH`,
`track-budget` → `TRACK_BUDGET`. Full list in [`../../action.yml`](../../action.yml).

`BUDGET_GCO2E` is the only required one. Two are worth knowing about here:

- **`MANIFEST_PATH`** — point it at a Deployment/StatefulSet manifest and the
  replica count and resource requests are read from it. On the Kubernetes
  platforms (Devtron, Northflank, Tekton, Argo, Spacelift) that beats declaring
  the same numbers twice and watching them drift apart.
- **`CI_API_AREA`** — an ISO country code (`SE`, `IT`, `US`) prices the deploy
  on that grid's live carbon intensity instead of a fixed `GRID_INTENSITY`. No
  credentials, no account. `EM_ZONE` + `EM_TOKEN` do the same through
  Electricity Maps if you already have a token.

## Outputs

Three of the action's outputs are GitHub-only plumbing and no-ops elsewhere:
`GITHUB_OUTPUT`, `GITHUB_STEP_SUMMARY`, and `PR_COMMENT` (which needs the GitHub
API). Everywhere else, the summary goes to **stdout** as markdown and the
verdict is the **exit code**:

| exit | meaning |
|---|---|
| `0` | within budget, or `MODE=report` |
| `1` | over budget in `gate` mode |

Most of the files below `tee` that markdown into an artifact, since a summary
that only exists in a log line is a summary nobody reads.

Start with `MODE=report`: it prints the estimate and never fails. Turn the gate
on once the number stops surprising people.

## Platform notes

**GitLab CI** — the job is scoped to merge requests with `rules:`. To gate the
deploy rather than the MR, move it to a `needs:`-linked job in the deploy stage.

**CircleCI** — runs on every push through the `pull-request` workflow. For a
nightly estimate instead, create a scheduled pipeline in project settings and
gate the workflow on `when: { equal: [scheduled_pipeline, << pipeline.trigger_source >>] }`.

**Travis CI** — set the numbers as repository environment variables (Settings →
Environment Variables) rather than in the file if a budget change shouldn't need
a commit.

**Azure DevOps** — `pr:` triggers only fire for Azure Repos. For a GitHub repo,
build validation is configured on the branch policy instead, and the `pr:` block
is ignored.

**AWS CodePipeline** — the gate is a CodeBuild action in a stage of its own,
ahead of Deploy. A failing build fails the stage and the pipeline stops there;
nothing rolls back, because nothing was deployed. Secrets, if you add any, come
from `env/secrets-manager` in the buildspec.

**Devtron** — a Pre-Deployment task, so an over-budget deploy is stopped before
the chart is applied. Devtron renders the Helm values you already maintain, so
prefer `MANIFEST_PATH` over restating replicas and requests in the task.

**Northflank** — a manual job, run as a step in the environment's release
workflow ahead of the deploy step. A failed step stops the rest of the workflow.
The JSON mirrors the API request body for `POST /v1/projects/{projectId}/jobs`;
the fields under `deployment.docker` are the *Docker configuration* section of
the job's UI, so if a field name has moved, that panel is the source of truth.

**Spacelift** — `before_apply` is the phase that matters: the plan has resolved
what the infrastructure will be, and nothing has been created yet. A hook
command exiting non-zero fails the run before apply. The default runner image
has no Python, hence `runner_image:`.

**Jenkins** — `agent { docker { … } }` needs the Docker Pipeline plugin; on an
agent that already has Python, `agent any` and drop the block.

**Bitbucket Pipelines** — the step is a YAML anchor so the same definition
serves both the pull-request trigger and a schedulable `custom:` pipeline.

**Google Cloud Build** — `${_ARTIFACT_BUCKET}` is a substitution; set it on the
trigger or delete the `artifacts:` block. Build triggers fire on push and PR;
Cloud Scheduler covers a periodic run.

**Tekton** — the Task takes a `source` workspace only so `MANIFEST_PATH` can
resolve against a checkout. Without manifests, drop the workspace and pass
`replicas`/`cpu-request`/`memory-request`.

**Argo Workflows** — the DAG is the gate: `deploy` depends on `carbon-budget`,
so a failed gate leaves it unrun. As a `CronWorkflow` the same template tracks
the estimate over time instead.

**Harness** — a `Run` step in a CI stage. `image:` on the step is optional on
Harness Cloud (the VM has Python); on Kubernetes build infrastructure the step
needs a `connectorRef` to whichever registry serves the image.

**Buildkite** — needs the `docker` plugin only to pin the Python version; an
agent with Python 3.10+ can run the commands directly. The estimator's output is
already markdown, so it feeds `buildkite-agent annotate` unchanged.

**Drone / Woodpecker** — the same steps run on both. Woodpecker drops the
`kind`/`type`/`name` header and the file is `.woodpecker.yml`.
