+++
date = 2023-04-10
title = "GitHub Actions 中是否可以只运行 pull request 中更改的 Playwright 测试?"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

你是否在 review 同事的 GitHub pull request 时,曾问自己这个 Playwright 测试是否能通过?我就有过这样的经历,这也是促使我写这篇文章的原因。在我的工作环境中,我希望防止失败的测试进入自动化测试的主干分支,但同时也不想运行每一个 spec 文件而导致反馈延迟,所以我用以下方法解决了这个问题。

在我的情况下,我使用专门的代码库进行自动化测试,主要用于回归测试。我有一个`main`代码分支,任何新添加到代码库的代码都将通过`pull request`合并进来。这要求开发人员从`main`分支创建一个新分支,编写、编辑或删除代码,然后创建一个指向 main 分支的`pull request`。我们将在这个`pull request`事件触发时做一些事情。

对我来说,这样做的好处包括:

- 当我最初创建 pull request 时,我可以确信我在本地编写和运行的测试也能在 CI 中通过。
- 我请求对 pull request 进行代码 review 的同事可以快速看到我修改的测试已运行并通过。
- 对于包含数百或上千个测试的测试套件,在 pull request 时只运行更改的文件可以提供更快的反馈,而不是等待所有测试运行完毕。

这个自动化测试逻辑主要做以下几件事：

1. 找出变化的文件：

   - 使用`git diff`命令比较`main`分支和新建的`my_new_branch`分支。
   - 这样可以得到两个分支之间所有变化的文件列表。

2. 筛选测试文件：

   - 从变化的文件中，只保留文件名包含".spec.ts"的文件。
   - 这些通常是 Playwright 的测试文件。

3. 保存文件列表：

   - 将筛选出的文件名列表（用空格分隔）保存到一个叫`CHANGED`的环境变量中。

4. 设置正确的 Git 历史深度：

   - 在 GitHub Actions 中，需要设置`actions/checkout`的`fetch-depth`为 0。
   - 这样做是为了确保 GitHub Actions 可以访问所有分支的完整历史。
   - 如果不这样设置，使用默认值 1 可能会导致`git diff`命令失败，错误信息为"fatal: Invalid revision range"。

5. 关于历史深度的说明：
   - 随着项目变大，你可以根据需要调整`fetch-depth`的值。
   - 但要记住，设置得太小可能会导致某些操作失败。

![图片 1](https://playwrightsolutions.com/content/images/2023/04/image-2.png)

GitHub Actions 日志 👆

以下是一个 GitHub actions .yml 文件的示例,展示了如何实现这一功能。

```yaml
# .github-ci.yml

name: Playwright API Checks

on:
  pull_request:
  workflow_dispatch:
    inputs:
      base_url:
        description: "URL, to run tests against"
        required: true
        default: https://automationintesting.online/

jobs:
  playwright-automation-checks:
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

      - name: Install node_modules and Playwright
      - run: npm ci --ignore-scripts
      - run: npx playwright install --with-deps
      - run: npx playwright install-deps

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
          URL=${{ env.BASE_URL}} npx playwright test --workers=1 ${{ env.CHANGED }}
```

需要注意的是,如果没有找到匹配`spec.ts`的文件,在运行`npx playwright test --workers=1 ${{ env.CHANGED}}`命令时,`CHANGED`变量将为空,所有测试都会运行(这对我来说是可以接受的)。

这种方法存在一个潜在的问题：

1. 分支同步问题：

   - 假设你正在一个特性分支上工作，准备创建 pull request。
   - 如果在此期间，main 分支有了新的更新，而你的特性分支还没有合并这些更新。

2. 可能的后果：

   - 使用`git diff`命令时，它会显示出所有的差异。
   - 这包括 main 分支上的新更改，即使这些更改与你的工作无关。

3. 影响：

   - 这可能导致运行一些不必要的测试，因为系统会认为这些文件也被修改了。

4. 替代方案：

   - 我的第一个解决方案使用了 GitHub API。
   - 使用 GitHub API 可以更精确地获取只在当前 pull request 中更改的文件。

5. 适用场景：
   - 对于小团队来说，这个问题可能影响不大。
   - 但对于大型团队，特别是 main 分支频繁更新的项目：
     - 使用 GitHub API 的方法可能更合适。
     - 它可以更准确地识别实际更改的文件，避免运行不必要的测试。

总的来说，这个问题在小团队中可能不太明显，但在大型、快节奏的开发环境中，使用更精确的 GitHub API 方法可能会带来显著的效率提升。

![图片 2](https://playwrightsolutions.com/content/images/2023/04/image.png)

### 我的第一个解决方案

当我第一次实现这个功能时,我的 Create Test List if pull_request 部分看起来很不一样。下面是代码,我使用了 GitHub API,发送 curl 请求获取完整的更改文件列表。这需要我在 GitHub 中创建一个个人访问令牌,并将其作为密钥添加到 GitHub Actions 中。

```yaml
- name: Create Test List if pull_request
  if: github.event.pull_request
  run: |
    echo "Creating a list of tests that have changed"
    FILES=$(curl --header "Authorization: Bearer ${{ secrets.REPO_ACCESS_TOKEN }}" --request GET 'https://api.github.com/repos/${{ github.repository }}/pulls/${{ github.event.pull_request.number }}/files' | jq -r '.[] | .filename' | grep "spec.ts" |  tr '\n' ' ')
    echo "CHANGED=$FILES" >> $GITHUB_ENV
```

感谢阅读!如果你觉得这篇文章有帮助,请在[LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew)上联系我,或考虑[为我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想在收件箱中收到更多内容,请在下方订阅。

## 来源

URL 来源: https://playwrightsolutions.com/is-it-possible-to-run-only-playwright-tests-that-changed-on-a/

发布时间: 2023-04-10T12:30:50.000Z
