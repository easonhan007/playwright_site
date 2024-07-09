+++
date = 2024-07-09
title = "如何在Playwright中使用分片"
description = "sharding也就是分片技术会让playwright的执行速度更快，另外本文也描述了如何在Github Actions里使用分片技术"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

大家好，在这篇简短的文章中，我们将探讨如何在 Playwright 中使用分片功能，将我们的测试分配到不同的分片上，以加快测试执行速度并减少 CI 流程中的总体运行时间。让我们开始吧，但首先我想介绍一下 Playwright 中的并行性。

![Image 3](https://miro.medium.com/v2/resize:fit:700/0*GOWzNZR8Lzry7bA4.jpeg)

## 并行性

在 Playwright 中，我们可以并行运行测试，这在 playwright.config.js 文件中默认设置为 true。启用此功能后，它会同时运行多个工作进程。单个文件中的测试按顺序在同一工作进程中运行。

![Image 4](https://miro.medium.com/v2/resize:fit:700/1*_b_72yxV15dfqt3y5lN3Wg.png)

并行测试还会在单独的工作进程中执行，无法共享任何状态或全局变量。还有很多方法可以配置测试以并行运行，如下所述：

1. 使用 test.describe.configure({ mode: ‘parallel’ });
2. 我们可以使用 fullyParallel: true 来为所有测试启用并行性
3. 或者我们可以为某些项目（如 chromium、firefox、webkit 等）启用 fullyParallel: true

要禁用并行性，我们可以通过配置文件将工作进程设置为 1，或者在使用 npx playwright test — workers=1 时从命令行传递相同的参数。

有关并行性的更多信息，请参阅此[页面](https://playwright.dev/docs/test-parallel)。

## 什么是分片？

“分片”这个词源自数据库架构概念，在该概念中，我们将大型数据库分成多个块或分片，以分散负载、优化工作负载、提高系统的效率和可扩展性。这有点类似于水平扩展，每个分片作为独立的单元，有自己的资源，并相应地管理数据，以提高查询性能，消除单独数据库服务器处理大量数据时的单点故障。

> 您可以在[这里](https://www.geeksforgeeks.org/database-sharding-a-system-design-concept/?ref=lbp)阅读更多关于分片的信息，此外，Gaurav Sen 有一个很棒的视频解释了这一点，请参考[视频](https://www.youtube.com/watch?v=5faMjKuB9bc)。

现在，回到 Playwright 世界，这里的分片概念可以用于通过将测试数量分散到多个分片或多台机器上同时运行来提高整体测试执行时间。我们可以使用 shard 参数来实现这一点，即 shard=x/y，其中 x 是分片索引，y 是总分片数。

npx playwright test --shard=1/4  
npx playwright test --shard=2/4  
npx playwright test --shard=3/4  
npx playwright test --shard=4/4

_在这里，我们将总测试分成 4 个分片，因此配置的工作进程将分别处理这些分片，以显著减少总体测试执行时间。_

_为了演示，我在本地机器上安装了 playwright，并将使用 tests-examples 文件夹中提供的示例代码进行测试，其中配置了一些测试在 playwright to-do mvc 网站上运行（URL:_ [_https://demo.playwright.dev/todomvc_](https://demo.playwright.dev/todomvc)_)。我们有大约 24 个测试，在 3 个浏览器上运行，总共 72 个测试文件，我复制了相同的文件两次，所以 3 个规范文件中有 216 个测试，分别在 3 个浏览器—chromium、firefox 和 webkit 上运行。我根据下图重命名了这些规范文件。_

![Image 5](https://miro.medium.com/v2/resize:fit:700/1*tieN5wq7GB8dLZf0VJtTJg.png)

在 playwright.config.js 中，我设置了以下配置，将并行设置为 true，工作进程数量为 6。

```javascript
fullyParallel: trueworkers: process.env.CI ? 6 : 6;
```

这意味着当我运行命令：npx playwright test 时，所有 216 个测试将在我的本地和 CI 中使用 6 个工作进程运行。以下测试在本地机器上使用 6 个工作进程运行。

![Image 6](https://miro.medium.com/v2/resize:fit:700/1*L_yIK08NCHk74_SbErufnw.png)

现在，如果我运行命令 npx playwright test，并指定总分片数为 4，首先将 216 个测试分为 4 个块，每个块包含 54 个测试。然后，这些 54 个测试将在分片 1 中使用 6 个工作进程执行，54 个测试在分片 2 中使用 6 个工作进程执行，如下所示。由于每个分片将在其自己的代理机器上执行，并行级别更深，我们的测试将显著更快地执行，而不仅仅是使用默认配置的 6 个工作进程。

![Image 7](https://miro.medium.com/v2/resize:fit:700/1*tAoX6kbSn1njJs6d3EXLHA.png)

但是使用分片时，我们会遇到默认 html 报告选项的报告问题。测试执行后，当我们运行命令'npx playwright show-report'时，我们会看到生成的报告只显示最后运行的分片的详细信息，仅包含 54 个测试，如下所示。那么之前分片中执行的其余测试呢？

![Image 8](https://miro.medium.com/v2/resize:fit:700/1*0h9DJZmMPoLbe4QOJ15y5g.png)

为了解决这个问题，当我们使用分片时，需要将报告配置为‘blob’。默认情况下，每个分片会在一个名为 blob-report 的文件夹中生成自己的 blob 报告，然后我们需要合并所有这些分片的 blob 报告，以获取所有测试的综合报告。

```javascript
export default defineConfig({
  reporter: process.env.CI ? "blob" : "html",
});
```

要合并多个分片的报告，将 blob 报告文件放入一个目录，例如在我们的例子中`all-blob-reports`，然后最终 HTML 报告将在 playwright-report 文件夹中可用。

```bash
npx playwright merge-reports --reporter html ./all-blob-reports
```

## 在 CI 中使用 Github Actions 进行分片

现在，为了有效地使用分片，我们可以利用 CI 工具如 Github Actions，在这些工具中我们可以轻松设置并在多台代理机器上运行测试。为此，我们需要在 Github Actions 工作流文件中包括以下几点：

1. 在作业中添加一个带有矩阵选项的策略，包含 shardIndex 和 shardTotal 值。
2. 运行 npx playwright test 命令，指定 shardindex 和 shardTotal 选项。
3. 将单个分片的 blob 报告上传到 Github Actions 工作流工件中，以便 merge-report 作业可以拾取并生成综合 HTML 报告。

```yaml
name: Sharding Tests
on:
 push:
 branches: \[ main, master \]
 pull_request:
 branches: \[ main, master \]jobs:
 run-tests:
 timeout-minutes: 60
 runs-on: ubuntu-latest
 strategy:
 fail-fast: false
 matrix:
 shardIndex: \[1, 2, 3, 4, 5, 6 \]
 shardTotal: \[6\]
 steps:

- uses: actions/checkout@v3
- uses: actions/setup-node@v3
  with:
  node-version: 20

- name: Install dependencies
   run: npm ci

- name: Install Playwright Browsers
   run: npx playwright install --with-deps

- name: Run Playwright tests
   run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}

- name: Upload blob report to GitHub Actions Artifacts
   if: always()
   uses: actions/upload-artifact@v4
   with:
   name: blob-report-${{ matrix.shardIndex }}
   path: blob-report
   retention-days: 1
```

对于作业“run-tests”，我们将使用在矩阵下指定的总共 6 个分片，并将 fail-fast 设置为 false。然后我们将使用特定的 shardIndex 和 shardTotal 值执行 npx playwright test，例如 1/6、2/6 等。最后，一旦分片执行完毕，单个分片的 blob 报告将上传到 actions 工件中，名称为 blob-report 并带有 shardIndex 后缀。

接下来，我们需要添加一个“merge-reports”作业，该作业将依赖于 run-tests 作业。此作业将下载所有单个分片的 blob 报告到一个指定的文件夹中，名为 all-blob-reports，然后运行 merge-reports 命令以获取综合 HTML 报告并将其上传到 GitHub Actions 工件选项卡中。

```yaml
merge-reports:
if: always()
needs: \[run-tests\]runs-on: ubuntu-latest
steps:

- uses: actions/checkout@v3
- uses: actions/setup-node@v3
  with:
  node-version: 18
- name: Install dependencies
  run: npm ci

- name: Download blob reports from GitHub Actions Artifacts
  uses: actions/download-artifact@v4
  with:
  path: all-blob-reports
  pattern: blob-report-\*
  merge-multiple: true

- name: Merge into HTML Report
  run: npx playwright merge-reports --reporter html ./all-blob-reports

- name: Upload HTML report
  uses: actions/upload-artifact@v4
  with:
  name: html-report--attempt-${{ github.run\_attempt }}
  path: playwright-report
  retention-days: 7
```

> 这是我的完整工作流文件及其所有作业 👇

```yaml
name: Playwright tests using sharding
on:
push:
branches: \[ main, master \]
pull_request:
branches: \[ main, master \]
jobs:
run-tests:
timeout-minutes: 60
runs-on: ubuntu-latest
strategy:
fail-fast: false
matrix:
shardIndex: \[1, 2, 3, 4, 5, 6 \]
shardTotal: \[6\]
steps:

- uses: actions/checkout@v3
- uses: actions/setup-node@v3
  with:
  node-version: 20
- name: Install dependencies
  run: npm ci
- name: Install Playwright Browsers
  run: npx playwright install --with-deps
- name: Run Playwright tests
  run: npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}- name: Upload blob report to GitHub Actions Artifacts
  if: always()
  uses: actions/upload-artifact@v4
  with:
  name: blob-report-${{ matrix.shardIndex }}
  path: blob-report
  retention-days: 1

merge-reports:
if: always()
needs: \[run-tests\]

runs-on: ubuntu-latest
steps:

- uses: actions/checkout@v3
- uses: actions/setup-node@v3
  with:
  node-version: 18
- name: Install dependencies
  run: npm ci

- name: Download blob reports from GitHub Actions Artifacts
  uses: actions/download-artifact@v4
  with:
  path: all-blob-reports
  pattern: blob-report-\*
  merge-multiple: true

- name: Merge into HTML Report
  run: npx playwright merge-reports --reporter html ./all-blob-reports

- name: Upload HTML report
  uses: actions/upload-artifact@v4
  with:
  name: html-report--attempt-${{ github.run\_attempt }}
  path: playwright-report
  retention-days: 7
```

一旦工作流文件被推送到 Github，所有总测试：216 将被分布并在我们的案例中 6 台机器上的特定分片机器上运行。如下所示，36 个测试在 run-tests (1,6)机器上执行。同样，其他分片代理机器上也会使用 6 个工作进程执行 36 个测试。一旦所有测试执行完毕，merge report 作业将被触发，然后生成我们的综合 HTML 报告。

![Image 9](https://miro.medium.com/v2/resize:fit:700/1*_prdug4U48kZ06C-voWX_Q.png)

![Image 10](https://miro.medium.com/v2/resize:fit:700/1*8ZCSRXOpVrQaSaTsvzFj1Q.png)

👇 以下是作为工作流运行的一部分上传的工件，单个分片的 blob 报告和最终的综合 html 报告。

![Image 11](https://miro.medium.com/v2/resize:fit:700/1*vkESn66s1bdwGXg5MqryBw.png)

下载并打开报告后，您会发现完整的测试运行报告，👇 其中包含在 6 台分片机器上执行的 216 个测试。

![Image 12](https://miro.medium.com/v2/resize:fit:700/1*rVylBxPlPxcdyeJv5LkfNg.png)

这就是您可以在您的 Playwright 设置中使用分片的方法。感谢阅读，希望您觉得这篇文章有用！

## 来源

[原文](https://blog.devops.dev/using-sharding-with-playwright-a94e54314b75?gi=f1526f73b9b4)

发布时间: 2024-03-01
