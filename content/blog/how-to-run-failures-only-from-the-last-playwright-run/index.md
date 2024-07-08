+++
date = 2024-07-07
title = "如何通过CLI仅运行上次Playwright运行中的失败"
description = "省流/TLDR; npx playwright test --last-failed"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

# 如何通过 CLI 仅运行上次 Playwright 运行中的失败

Hello Playwright [1.44](https://playwright.dev/docs/release-notes#version-144)版本发布！在这个版本中，我们现在可以官方支持仅运行上次 Playwright 运行中的失败测试。

💡TLDR; `npx playwright test --last-failed`

<div class="w-full md:w-1/3 mx-auto">
<img src="https://playwrightsolutions.com/content/images/2024/06/happy.gif" />
</div>

## 以前的解决方案

去年，我创建了 json 摘要报告器和一个 bash 脚本，可以在下面的文章中找到。这是我为了能够轻松重新运行失败测试而创建的解决方案。我仍然认为我创建的工具具有很大的价值，特别是当我在 CI 中遇到失败时，我可以快速复制我的 json 摘要结果并将其粘贴到我的本地`summary.json`文件中，然后在本地运行失败的测试进行调试。请参阅下面的文章以了解更多信息。

[在 Playwright 测试完成后仅重新运行失败测试的最简单方法是什么？在所有关于重试失败的精彩功能中，我发现自己需要一种简单的方法来重新运行最近一次运行中的所有测试。这与测试重试和断言重试不同，因为那些是在完成重试的情况下进行的。](https://playwrightsolutions.com/whats-the-easiest-way-to-only-re-run-failures-after-the-playwright-test-is-finished/)

## 当前的解决方案

但真正令人兴奋的是，我现在可以使用这个新的 CLI 命令重新运行我上次运行中的失败测试。首先，您需要确保您的 Playwright 版本至少为 1.44。您可以通过查看`package.json`来检查。

![Image 4](https://playwrightsolutions.com/content/images/2024/06/image-1.png)

在这个例子中，我创建了一些每次运行时会失败一半的测试来演示这个功能。在运行`npx playwright test`之后，我看到了这些结果。

![Image 5](https://playwrightsolutions.com/content/images/2024/06/image-4.png)

我现在可以运行命令`npx playwright test --last-failed`，这将重新运行上次运行中失败的 1 个测试。在下面的情景中，测试失败了，但在“重试”时通过了。这表明`--last-failed`命令将会列队上次运行中失败状态的所有测试。

![Image 6](https://playwrightsolutions.com/content/images/2024/06/image-5.png)

## 引用

[原文](https://playwrightsolutions.com/how-to-run-failures-only-from-the-last-playwright-run/)

更新日期: 2024-06-03
