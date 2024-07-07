+++
date = 2024-07-07
title = "如何让 playwright 运行的更快"
description = "使用这些技术可以让 playwright 运行速度快 10 倍"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.avif"
+++

在这篇文章中，我将解释如何使用 Playwright 将测试速度提高**至少 10 倍**。

首先，让我们来了解一下什么是 Playwright。

Playwright 是一个 Node.js 库，它允许你使用相同的 API 脚本和自动化浏览器，如 Chrome、Firefox 和 Safari。

如果你想知道为什么要使用 Playwright，可以看看这个[链接](https://www.devstringx.com/playwright-tool)。现在让我们通过一个例子来看看如何使用 Playwright 加速测试。

## 并行化

加速测试的一种方法当然是并行运行。首先，我们打开一个名为 example.spec.ts 的文件，放入 20 个测试用例，并在每个测试用例中写入以下代码，让其静态等待 30 秒。

```javascript
await new Promise((resolve) => setTimeout(resolve, 30000));
```

这个数字将帮助我们理解通过并行运行获得的收益。我们的文件最终版本如下。

```javascript
test.describe("20个示例测试", () => {
  test('测试 - 1', async ({ page }) => {
    await new Promise(resolve => setTimeout(resolve, 30000));
  });
  test('测试 - 2', async ({ page }) => {
    await new Promise(resolve => setTimeout(resolve, 30000));
  });
  test('测试 - 3', async ({ page }) => {
    await new Promise(resolve => setTimeout(resolve, 30000));
  });
  .
  .
  .
  test('测试 - 19', async ({ page }) => {
    await new Promise(resolve => setTimeout(resolve, 30000));
  });
  test('测试 - 20', async ({ page }) => {
    await new Promise(resolve => setTimeout(resolve, 30000));
  });
});
```

如果我们一个一个地运行这些测试（是的，你猜对了！）需要 10 分钟。

![图片3](https://miro.medium.com/v2/resize:fit:700/1*VIOOJ8QIkBLAKmhlUHsJNQ.png)

20 个测试一个一个运行需要 10 分钟

10 分钟对于每个运行 30 秒的 20 个测试用例来说太多了。让我们把这个时间缩短一些。Playwright 使用同时运行的工作进程来并行运行。让我们用 5 个工作进程并行运行这些测试，看看区别。

![图片4](https://miro.medium.com/v2/resize:fit:700/1*SDe6gpDyOrqSsTPP8G5-ow.png)

20 个测试用 5 个工作进程运行需要 2 分钟

是的，我们成功地用 5 个工作进程在 2 分钟内运行了 20 个测试。这里我们用了 5 个工作进程作为例子，但你可以根据你的系统增加或减少这个数量，直到找到最适合你的测试数量。

那么我们能跑得更快吗？5 倍的加速对我们来说够了吗？当然不够，我们需要更快。那么我们该怎么做呢？让我们看看 Playwright 的分片定义。

## 分片

如果我们使用多台机器，每台机器上分配相同数量的测试用例并并行运行，会怎么样？听起来不错。为此，Playwright 为我们提供了分片功能。

![图片5](https://miro.medium.com/v2/resize:fit:609/1*Kb2TJi5VqpR20C3A5d2CQg.png)

用分片运行 20 个测试

在同一台机器上，我们将测试用例分成 5 个相等的部分，并进行 4 次并行运行。如果我们在 5 台不同的机器上运行这些命令，所有测试用例将在 30 秒后运行完毕。这意味着本来需要 10 分钟逐一运行的所有测试用例现在可以在 30 秒内运行完成。不可思议吧？

```bash
npx playwright test - shard=index/total-shard
```

在这里你可以根据你拥有的机器数量划分资源。我这里举了 5 个的例子。

## Gitlab 集成

让我们在 Gitlab 中创建一个流水线并在 5 台机器上试一试。创建一个.gitlab-ci.yaml 文件，让我们开始吧。

```yaml
stages:
  - test
tests:
  stage: test
  image: mcr.microsoft.com/playwright:v1.38.0-focal
  parallel:
    matrix:
      - SHARD_INDEX: [1, 2, 3, 4, 5]
        SHARD_TOTAL: 5
  script:
    - npm ci
    - npx playwright test --shard=$SHARD_INDEX/$SHARD_TOTAL
```

我们使用“npm ci”命令安装我们的依赖项。

然后我们通过运行“npx playwright test — shard=$SHARD_INDEX/$SHARD_TOTAL”命令来运行测试。让我们看看等待我们的是什么。

![图片6](https://miro.medium.com/v2/resize:fit:700/1*mazgQFSwmx7mD2vt8-6_ag.png)

流水线

![图片7](https://miro.medium.com/v2/resize:fit:700/1*dQKvVzT6FubEToBz66cwJw.png)

总共 5 个作业

![图片8](https://miro.medium.com/v2/resize:fit:700/1*J4MLmw-mSN-lk0RSSWvlTA.png)

第一个作业的详细信息

正如你在这里看到的，流水线在大约 1 分钟内完成了 5 个并行运行的作业。实际上，测试运行了 30 秒，剩下的时间是环境准备时间，如你在截图中看到的。实际上，它从 10 分钟变成了 30 秒。

通过使用 Playwright 的工作进程和分片功能，你可以在短时间内运行大量测试用例。下次文章再见！

## 原文地址

[这里](https://hasangurhan.medium.com/how-did-i-run-tests-at-least-10x-faster-with-playwright-c25687982caf)
