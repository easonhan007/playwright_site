+++
date = 2022-03-14
title = "在 Playwright Test 中有简便的方法重复执行测试多次来检查用例的稳定性吗？"
description = "省流: --repeat-each"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在 Playwright Test 中有简便的方法重复执行测试多次来检查用例到底稳定不稳定性吗？

我发现在合并新代码到测试集的主干分支之前，在 pull request 上多次运行新的自动化测试或对现有测试的进行修改是一个很好的做法，这样可以检查测试的不稳定性。要实现这一点，你可以构建 CI 流水线来运行命令 `npx playwright test --repeat-each=5`。关于命令行运行的文档可以在[这里](https://playwright.dev/docs/test-cli)找到。

你还可以更进一步，通过 git 比较查看哪些目录发生了变化，并将目录作为参数传递给命令。下面这个命令将会运行 todo-page 和 landing-page 目录下的所有测试，每个测试重复 5 次：`npx playwright test tests/todo-page/ tests/landing-page/ --repeat-each=5`

如果这个解决方案对你有帮助，欢迎点赞支持！

## 来源

URL 来源：https://playwrightsolutions.com/in-playwright-test-is-there-an-easy-way-to-loop-the-test-multiple-times-to-check-for-flakiness/

发布时间：2022 年 3 月 14 日 21:12:45
