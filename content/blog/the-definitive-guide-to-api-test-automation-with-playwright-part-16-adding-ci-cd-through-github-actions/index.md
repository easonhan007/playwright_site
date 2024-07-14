+++
date = 2023-11-27
title = "The Definitive Guide to API Test Automation With Playwright: Part 16 - Adding CI/CD Through GitHub Actions"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

This is the final planned article of this series, where we will discuss Adding CI/CD through GitHub Actions. In this guide I'll walk through the basics of GitHub Actions along with ways you can scale your tests as the suite grows.

If you're just joining us now go check out the [introduction post](https://playwrightsolutions.com/is-it-possible-to-do-api-testing-with-playwright-the-definitive/) which links to all parts we've covered so far. For our examples we will use the playwright-api-test-demo repository linked below.

[GitHub - playwrightsolutions/playwright-api-test-demo](https://github.com/playwrightsolutions/playwright-api-test-demo)

For this guide I'm using [GitHub Actions](https://docs.github.com/en/actions). You can think of GitHub Actions  yml files which I'll provide below as your instructions on what code you want to run in the cloud, via [GitHub hosted runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners/about-github-hosted-runners). I'll use GHA in place of GitHub Actions going forward. With each example there are 4 primary areas that are needed for a GHA yml file, which include:

- **name** - Name of the GHA that shows up in the web portal.
- **on** - How and when to run the GHA.
- **permissions (optional)** - What permissions should the hosted runners run with.
- **jobs** - What software/libraries and commands will be run.

I'll be walking through the two different GHA workflows I have built for this project. The first will run the full suite daily and on demand while the other one will run a subset of tests that changed from a pull request. What this article won't cover is:

1.  How to [run your tests multiple times to check for flakiness](https://playwrightsolutions.com/in-playwright-test-is-there-an-easy-way-to-loop-the-test-multiple-times-to-check-for-flakiness/). this can easily be implemented in the on pull request job by adding `repeat-each=5` within the npx playwright command.
2.  How to make a [GHA from another repository trigger the Playwright Tests to run on this repo.](https://playwrightsolutions.com/how-do-i-trigger-playwright-tests-to-run-across-repositories-using-github-actions/) I've written about this in the past, and it's worth looking into if that is a problem you are trying to solve. This is very useful if you have your automation code in a separate repository than the web application code your testing against.

Now on with the show!

## Full Suite Daily Runs

This first action is really the bread and butter of our CI (Continuous Integration) Pipeline. It will run once a day (early in the morning) to give us constant feedback as changes happen throughout the day. I like the early AM run time as I wake up to the results of the entire test suite, and can plan my morning accordingly.

Below I'll walk through the different sections of the GHA yml file, below you can see the entire workflow file.

The first sections include the **name**, **on**, and **permissions** blocks.

```yaml
name: Daily Playwright API Checks

on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:
    inputs:
      base_url:
        description: "URL, to run tests against"
        required: true
        default: https://automationintesting.online/
permissions:
  contents: write
  pages: write
  id-token: write
```

The **on** section includes a ton of options that can be used in initiating the job. The [docs](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows) show off 35 different ways to trigger a GHA as I'm writing this, I'm sure there will be more added as GHA is still a relatively new tool, as it's only bee in the wild for 5 years.

In my on section I have a **schedule** section which will run the job via [cron](https://crontab.guru/#0_6_*_*_*), every morning at 6:00 AM. I also have a **workflow_dispatch** section with some inputs. This allows me to [run my job](https://github.com/playwrightsolutions/playwright-api-test-demo/actions/workflows/daily-full.yml) adhoc and pass in a different base_url if needed.

![Image 3](https://playwrightsolutions.com/content/images/2023/11/image-5.png)

The permission section is necessary as I want to publish my artifacts to GitHub Pages so I can view my latest run's trace file for better debugging.

The next section focuses on **jobs.** The first entry is the name of the job that will be run, where I also setup environment variables for the entire suite if needed. The specific environment settings were for the GHA pages step. I also have a hard timeout-minutes of 10. This will ensure that if the job is for some reason running longer than 10 minutes to time it out. I am also running this on ubuntu-latest Operating System. The final section is an `env` variable where I am setting BASE_URL to the input `base_url` for workflow_dispatch runs, where I specify a different URL to run against.

```yaml
jobs:
  playwright-automation-checks:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    timeout-minutes: 10
    runs-on: ubuntu-latest

    env:
      BASE_URL: ${{ github.event.inputs.base_url }}
```

The rest of the GHA file is all about the `[steps](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions#jobs)` that are run as apart of the job.

> A job is a set of _steps_ in a workflow that is executed on the same runner. Each step is either a shell script that will be executed, or an _action_ that will be run. Steps are executed in order and are dependent on each other. Since each step is executed on the same runner, you can share data from one step to another. For example, you can have a step that builds your application followed by a step that tests the application that was built.

What's nice about steps is they are run in order, and are dependent on each other, so you can think of the steps as a list of what you want to accomplish.

### Checkout Code and Setup Environment

- Checking Out Code using [actions/checkout@v3](https://github.com/actions/checkout)
- Installing Node using [actions/setup-node@v3](https://github.com/actions/setup-node)
- Installing Node Dependencies and Caching OR Restoring Them From Cache using [actions/cache@v3](https://github.com/actions/cache)
- Installing Playwright and Caching OR Restoring From Cache using [actions/cache@v3](https://github.com/actions/cache)

Each of the setups in this section use a pre-made action that cane be found on the [GitHub Marketplace](https://github.com/marketplace?type=actions). Each of these have their own readme on how to use them in their respective repos linked above.

```yaml
steps:
  - uses: actions/checkout@v3
    with:
      fetch-depth: 0

  - uses: actions/setup-node@v3
    with:
      node-version: 16

  - name: Cache node_modules
    uses: actions/cache@v3
    id: node-modules-cache
    with:
      path: |
        node_modules
      key: modules-${{ hashFiles('package-lock.json') }}
  - run: npm ci --ignore-scripts
    if: steps.node-modules-cache.outputs.cache-hit != 'true'

  - name: Get installed Playwright version
    id: playwright-version
    run: echo "PLAYWRIGHT_VERSION=$(node -e "console.log(require('./package-lock.json').dependencies['@playwright/test'].version)")" >> $GITHUB_ENV

  - name: Cache playwright binaries
    uses: actions/cache@v3
    id: playwright-cache
    with:
      path: |
        ~/.cache/ms-playwright
      key: ${{ runner.os }}-playwright-${{ env.PLAYWRIGHT_VERSION }}
  - run: npx playwright install --with-deps
    if: steps.playwright-cache.outputs.cache-hit != 'true'
  - run: npx playwright install-deps
    if: steps.playwright-cache.outputs.cache-hit != 'true'
```

One quick note if you use Webkit/Safari for testing, you may run into issues, I would recommend not caching playwright if this is the case.

### Running Tests

For the next set of steps I am only including a `name` and `run` with the associated command that I want to run. The GHA runner has node installed and has playwright and the project dependencies installed already so we are good to just run the same commands you would from your local machine.

- Run linter
- Run prettier
- Run unit tests

When setting the BASE_URL environment, I am actually first checking if the `env.BASE_URL == null` then set it with a value. If there is any other value, this set doesn't get executed.

- Set BASE_URL if null

This section I am setting up `env` variables that re needed for this step, along with a multi-line command. The first is just echoing the github event name (more for debugging purposes, it's not needed for the job to suceed) and the 2nd is the `npm run test` command which will run our tests with the following command (this is found in the package.json file in the `scripts` section.

![Image 4](https://playwrightsolutions.com/content/images/2023/11/image-6.png)

- Setup Environment Variables for [Currents.Dev](https://currents.dev/playwright?utm_source=pw_solutions_cicd) (I'm cooking up an article for this service!)
- Run Playwright tests

```yaml
- name: Run lint
  run: npm run lint
- name: Run prettier
  run: npm run prettier
- name: Run UnitTests
  run: npm run ut

- name: Set BASE_URL if not passed in
  if: env.BASE_URL == null
  run: |
    echo "BASE_URL=https://automationintesting.online/" >> $GITHUB_ENV

- name: Run Playwright tests
  env:
    CURRENTS_PROJECT_ID: ${{ secrets.CURRENTS_PROJECT_ID }}
    CURRENTS_RECORD_KEY: ${{ secrets.CURRENTS_RECORD_KEY }}
    CURRENTS_CI_BUILD_ID: reporter-${{ github.repository }}-${{ github.run_id }}-${{ github.run_attempt }}
    URL: ${{ env.BASE_URL}}
  run: |
    echo "The github event is: ${{ github.event_name }}"
    npm run test
```

### Publishing Results

- Setup GH Pages using [actions/configure-pages@v3](https://github.com/actions/configure-pages)
- Upload GHA Artifact `playwright-report` using [actions/upload-artifact@v3](https://github.com/actions/upload-artifact)
- Upload Pages Artifact using [actions/upload-pages-artifact@v1](https://github.com/actions/upload-pages-artifact)
- Deploy to Pages using [action/deploy-pages@v2](https://github.com/actions/deploy-pages)

Each of these sections are using the `use` functionality that leverage pre-built steps. 3 of the 4 steps above are all about configuring, uploading, and deploying the Playwright Report to GitHub Pages, while the 2nd setp Upload GHA Artifact will zip and upload the `playwright-report` and attach it to the GHA run. An example of this can be found on this [test run](https://github.com/playwrightsolutions/playwright-api-test-demo/actions/runs/6923995256). The bottom section has Artifacts that you are able to download assuming they haven't expired. This will include the html test report along with trace files and any assets (videos, images) that were captured as a part of the test run.

![Image 5](https://playwrightsolutions.com/content/images/2023/11/image-7.png)

```yaml
# The following steps are for deploying the report to GitHub Pages
- name: Setup Pages
  if: always()
  uses: actions/configure-pages@v3

- uses: actions/upload-artifact@v3
  if: always()
  with:
    name: report-artifact
    path: playwright-report/
    retention-days: 3

- name: Upload Pages Artifact
  uses: actions/upload-pages-artifact@v1
  if: always()
  with:
    path: "playwright-report/"

- name: Deploy to GitHub Pages
  if: always()
  id: deployment
  uses: actions/deploy-pages@v2
```

### The Full GHA workflow file

```yaml
//.github/workflows/daily-full.yml

name: Daily Playwright API Checks

on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:
    inputs:
      base_url:
        description: "URL, to run tests against"
        required: true
        default: https://automationintesting.online/
permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  playwright-automation-checks:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    timeout-minutes: 10
    runs-on: ubuntu-latest

    env:
      BASE_URL: ${{ github.event.inputs.base_url }}

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v3
        with:
          node-version: 16

      - name: Cache node_modules
        uses: actions/cache@v3
        id: node-modules-cache
        with:
          path: |
            node_modules
          key: modules-${{ hashFiles('package-lock.json') }}
      - run: npm ci --ignore-scripts
        if: steps.node-modules-cache.outputs.cache-hit != 'true'

      - name: Get installed Playwright version
        id: playwright-version
        run: echo "PLAYWRIGHT_VERSION=$(node -e "console.log(require('./package-lock.json').dependencies['@playwright/test'].version)")" >> $GITHUB_ENV
      - name: Cache playwright binaries
        uses: actions/cache@v3
        id: playwright-cache
        with:
          path: |
            ~/.cache/ms-playwright
          key: ${{ runner.os }}-playwright-${{ env.PLAYWRIGHT_VERSION }}
      - run: npx playwright install --with-deps
        if: steps.playwright-cache.outputs.cache-hit != 'true'
      - run: npx playwright install-deps
        if: steps.playwright-cache.outputs.cache-hit != 'true'

      - name: Run lint
        run: npm run lint
      - name: Run prettier
        run: npm run prettier
      - name: Run UnitTests
        run: npm run ut

      - name: Set BASE_URL if not passed in
        if: env.BASE_URL == null
        run: |
          echo "BASE_URL=https://automationintesting.online/" >> $GITHUB_ENV

      - name: Run Playwright tests
        env:
          CURRENTS_PROJECT_ID: ${{ secrets.CURRENTS_PROJECT_ID }}
          CURRENTS_RECORD_KEY: ${{ secrets.CURRENTS_RECORD_KEY }}
          CURRENTS_CI_BUILD_ID: reporter-${{ github.repository }}-${{ github.run_id }}-${{ github.run_attempt }}
          URL: ${{ env.BASE_URL}}
        run: |
          echo "The github event is: ${{ github.event_name }}"
          npm run test

      # The following steps are for deploying the report to GitHub Pages
      - name: Setup Pages
        if: always()
        uses: actions/configure-pages@v3

      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: report-artifact
          path: playwright-report/
          retention-days: 3

      - name: Upload Pages Artifact
        uses: actions/upload-pages-artifact@v1
        if: always()

        with:
          path: "playwright-report/"

      - name: Deploy to GitHub Pages
        if: always()
        id: deployment
        uses: actions/deploy-pages@v2
```

## Changed Files Only on Pull Requests Runs

Below is my GHA workflow that I run on pull requests that occure against the main branch. I'll walk through the differences below.

```yaml
// .github/workflows/on-pr.files-changed.yml

name: Changed Files Playwright API Checks

on:
  pull_request:
    branches:
      - main
permissions:
  contents: write
  pages: write
  id-token: write

jobs:
  playwright-automation-checks:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    timeout-minutes: 10
    runs-on: ubuntu-latest

    env:
      BASE_URL: ${{ github.event.inputs.base_url }}
      CHANGED: ""

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v3
        with:
          node-version: 16

      - name: Cache node_modules
        uses: actions/cache@v3
        id: node-modules-cache
        with:
          path: |
            node_modules
          key: modules-${{ hashFiles('package-lock.json') }}
      - run: npm ci --ignore-scripts
        if: steps.node-modules-cache.outputs.cache-hit != 'true'

      - name: Get installed Playwright version
        id: playwright-version
        run: echo "PLAYWRIGHT_VERSION=$(node -e "console.log(require('./package-lock.json').dependencies['@playwright/test'].version)")" >> $GITHUB_ENV
      - name: Cache playwright binaries
        uses: actions/cache@v3
        id: playwright-cache
        with:
          path: |
            ~/.cache/ms-playwright
          key: ${{ runner.os }}-playwright-${{ env.PLAYWRIGHT_VERSION }}
      - run: npx playwright install --with-deps
        if: steps.playwright-cache.outputs.cache-hit != 'true'
      - run: npx playwright install-deps
        if: steps.playwright-cache.outputs.cache-hit != 'true'

      - name: Run lint
        run: npm run lint
      - name: Run prettier
        run: npm run prettier
      - name: Run UnitTests
        run: npm run ut

      - name: Set BASE_URL if not passed in
        if: env.BASE_URL == null
        run: |
          echo "BASE_URL=https://automationintesting.online/" >> $GITHUB_ENV

      - name: Create Test List if pull_request
        if: github.event.pull_request
        run: |
          echo "Creating a list of tests that have changed"
          FILES=$(git diff --name-only ${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }} | grep ".spec.ts" | tr '\n' ' ')
          echo "CHANGED=$FILES" >> $GITHUB_ENV

      - name: Run Playwright tests
        run: |
          echo "CHANGED = ${{ env.CHANGED }}"
          echo "The github event is: ${{ github.event_name }}"
          URL=${{ env.BASE_URL}} npx playwright test --reporter=github --workers=1 ${{ env.CHANGED }}

      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: report-artifact
          path: playwright-report/
          retention-days: 3
```

The biggest difference is we won't plan on running all the playwright tests whenever there is a pull request, but only attempt to run files that were changed or added as a part of the pull request. Below are the big differences.

- Create a List of Tests That Have Been Added or Changed

This section utilizes a bash script in the `run` section to set variable FILES= to the difference between git shas where the filename ends in `.spec.ts` using `grep` and then replacing `\n` which is a new line (enter) with just a `' '` space.  I then export the FILES variable to `CHANGED` env variable.

- Run the Playwright Tests That Were Changed

Now that we have a list of files that have changed we can then pass those in at the end of the `npx playwright test` script.

```yaml
- name: Create Test List if pull_request
  if: github.event.pull_request
  run: |
    echo "Creating a list of tests that have changed"
    FILES=$(git diff --name-only ${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }} | grep ".spec.ts" | tr '\n' ' ')
    echo "CHANGED=$FILES" >> $GITHUB_ENV

- name: Run Playwright Tests
  run: |
    echo "CHANGED = ${{ env.CHANGED }}"
    echo "The github event is: ${{ github.event_name }}"
    URL=${{ env.BASE_URL}} npx playwright test --reporter=github --workers=1 ${{ env.CHANGED }}
```

This is an example of what the output for the `Run Playwright Tests` section looks like within GHA (the blue are the commands that were executed).

![Image 6](https://playwrightsolutions.com/content/images/2023/11/image-8.png)

You can see that the different test file names were saved properly into the env variable. The pro to this is you get faster feedback when you are updating your tests. The con is if you make a change to a non-spec file the `env.CHANGED` variable will be empty and your whole test suite will run (which may be ok in the end).

## Wrapping up

GitHub Actions is a great tool that is already integrated with GitHub in order to run your Playwright Tests, and the cost of GHA minutes is relatively inexpensive for most folks needs. This is one of the first things I spend effort on when building out my automated checks to ensure I get constant feedback either after pull requests or at least daily.

---

Thanks for reading! If you found this helpful, reach out and let me know on [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) or consider [buying me a cup of coffee](https://ko-fi.com/butchmayhew). If you want more content delivered to you in your inbox subscribe below, and be sure to leave a ❤️ to show some love.

## 来源

URL Source: https://playwrightsolutions.com/the-definitive-guide-to-api-test-automation-with-playwright-part-16-adding-ci-cd-through-github-actions/

Published Time: 2023-11-27T13:30:36.000Z
