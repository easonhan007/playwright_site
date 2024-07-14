+++
date = 2022-11-06
title = "如何使用 GitHub Action 触发另一个代码库中的 Playwright 测试?"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

如果你发现 Playwright 测试自动化代码与被测服务或应用程序位于不同的代码库中,别担心!本文将介绍如何通过 GitHub Actions 跨代码库触发测试运行。

虽然有多种方法可以实现这一目标,但最简单的方式是利用 GitHub Actions,特别是 `peter-evans/repository-dispatch@v2` [action](https://github.com/peter-evans/repository-dispatch)。这个 GitHub Action 可以让你轻松使用 [Repository Dispatch API](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#repository_dispatch) 来触发其他代码库中的 GitHub Actions。

唯一的前提条件是你需要创建一个具有 `repos` 权限的个人访问 token(PAT)。

创建个人访问 token 的步骤可以在[这里](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)找到。需要允许的权限范围如下图所示。

![图片 1](https://playwrightsolutions.com/content/images/2022/11/image.png)

保存后,你需要将 PAT 保存为应用程序代码库中的 GitHub Action Secret。在设置页面左侧,展开 Secrets 并查看 Actions 页面

![图片 2](https://playwrightsolutions.com/content/images/2022/11/image-2.png)

👆 代码库 > 设置 > Secrets > Actions

添加名为 `REPO_ACCESS_TOKEN` 的 PAT

![图片 3](https://playwrightsolutions.com/content/images/2022/11/image-3.png)

👆 将 PAT 添加到 Action secrets

## 编写 GitHub Action yml 文件

完成上述步骤后,你只需要编写 .yml 文件来启动 Repository Dispatch,并在测试代码库中设置 `on` repository_dispatch 来运行测试。以下是服务/应用程序代码库(你想要从中启动测试运行的地方)和接收代码库(运行测试的地方)的 GitHub Action yml 文件示例。

第一部分包括服务或应用程序的 yml 示例,以及一个可以查看实际运行情况的 GitHub 代码库链接。

_my-service 代码库中的 build-deploy.yml_

```yaml
name: My Service Build and Deploy
on:
  push:
    branches:
      - develop
jobs:
  deploy_staging:
    name: Staging Deploy
    runs-on: ubuntu-latest
    steps:
      - name: 记录 Staging 发布
        run: echo "这次运行是 staging 部署"
      - name: pull代码
        uses: actions/checkout@v2
      - name: 设置要传递给测试的 URL
        run: |
          echo "ENVIRONMENT=http://my-site.com" >> $GITHUB_ENV
      - name: 构建和部署
        run: |
          echo "构建和部署"
      - name: 触发 Playwright 测试作业
        uses: peter-evans/repository-dispatch@v2
        with:
          token: ${{ secrets.REPO_ACCESS_TOKEN }}
          repository: bmayhew/my-tests
          event-type: run-my-tests
          client-payload: '{"github": ${{ toJson(github) }}}'
```

[GitHub Action 运行示例](https://github.com/BMayhew/my-service/actions/runs/3397953921/jobs/5650587912)

[GitHub my-site 代码库](https://github.com/BMayhew/my-service)

关于这行 `client-payload: '{"github": ${{ toJson(github) }}}'` 的快速说明: 这允许你传递当前 GitHub 运行的所有详细信息(状态、环境变量、你想要设置或从作业的前面步骤传递到测试作业的任何内容)。我使用这个的方式包括发送预览环境 URL、GitHub 评论 ID、设置我正在进行的反馈/测试类型(快乐路径或完整运行)等。

---

这部分是 Playwright 测试代码库中应包含内容的示例。需要特别注意的行包括何时运行 GitHub Action `on` 以及创建与服务/应用程序 GitHub Action 中发送的 `event-type` 名称相匹配的类型。

```yaml
on:
  repository_dispatch:
    types: ["run-my-tests"]
```

_my-tests 代码库中的 run-tests.yml_

```yaml
name: Playwright 自动化测试
on:
  workflow_dispatch:
    inputs:
      environment:
        description: "要运行测试的 URL"
        required: true
        default: https://my-site.com
  repository_dispatch:
    types: ["run-my-tests", "run-my-tests-2"]
jobs:
  run_automation_tests:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    env:
      ENVIRONMENT: ${{ github.event.inputs.environment }}${{ github.event.client_payload.github.event.inputs.environment }}
    steps:
      - name: 运行 Playwright 测试
        run: |
          echo "环境: $ENVIRONMENT"
          echo "GitHub 事件是: ${{ github.event_name }}"
          echo "在这里运行测试"
          echo "Action 中的以下步骤提供了你可以在脚本中使用的内容"
      - name: 输出 GitHub 上下文
        id: github_context_step
        # 以下内容会打印出所有可用于任何报告或从其他代码库运行测试的信息
        run: echo '${{ toJSON(github) }}'
```

[GitHub Action 运行示例](https://github.com/BMayhew/my-tests/actions/runs/3397955085/jobs/5650589659)

[GitHub my-test 代码库](https://github.com/BMayhew/my-tests)

要访问 `client_payload` 中发送的任何详细信息,你必须调用:

`${{ github.event.client_payload.github.你想要的信息 }}`

如果你不确定想要什么,运行命令:

`echo '${{ toJSON(github) }}'`

这将在 GitHub Action 中输出一个 JSON 对象,包含你在 GitHub Action 中可以访问的所有不同键值对。

如果你想更进一步,可以继续使用 Repository Dispatch 功能向原始服务/应用程序代码库回传状态,根据测试是否通过执行不同的自动化操作。例如,你可以为特定的拉取请求添加标签,或创建一个操作来向拉取请求添加评论,说明测试的状态(你需要从 client_payload 中保留原始拉取请求 ID)。

---

关于跨代码库使用这种功能的可能性是无限的。希望你觉得这篇文章有帮助!如果你想出了使用 Repository Dispatch 的任何创意方法,或者觉得这篇文章有用,欢迎在 Twitter 上联系我 [@butchmayhew](https://twitter.com/ButchMayhew),或者考虑给我买杯咖啡。

## 来源

[URL 来源](https://playwrightsolutions.com/how-do-i-trigger-playwright-tests-to-run-across-repositories-using-github-actions/)

发布时间: 2022-11-06T04:32:48.000Z
