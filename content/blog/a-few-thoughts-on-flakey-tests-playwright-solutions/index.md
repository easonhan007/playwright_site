+++
date = 2024-06-10
title = "关于测试不稳定(flakey tests)的一些思考"
description = "省流：先搞清楚失败原因，实在不稳定，那么就删除掉这些用例"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

当一个新的测试自动化项目开始时，通常有 3 个工作重点。**构建**（创建新测试）、**维护**（随着应用程序变化更新现有测试）和**监控**（关注自动化运行情况，调查失败原因并向团队反馈发现）。

"不稳定"测试主要涉及自动化运行的"**监控**"部分。如果一个测试不稳定，深入了解原始测试失败的原因总是很重要的...这一点很关键，如果人们不采取这一步骤，可能会带来重大风险。

下面我将分享一些我在处理不稳定性方面的经验，这个列表绝不是全面的。

## 我认为的不稳定测试

- 由于陷入不良状态而失败的测试。例如，你期望处于登录状态，但实际上处于登出状态，或者可能另一个测试/用户修改了你正在断言的数据。
- 用于测试的数据质量不佳。例如，你发送了一个 11 位的电话号码，或者由于运行自动化的机器与你的本地时区不同，你发送了一个带有错误 UTC 偏移的日期时间戳。
- 自动化代码中是否存在竞争条件，在页面数据加载完成之前就尝试进行断言？
- 是否由于未正确实现 await 语法而导致测试超时？

> 调查每次失败是至关重要的。

对于这些场景中的每一个，仅仅因为测试偶尔失败并不意味着它是一个不稳定的测试。**调查每次失败是至关重要的**，确保问题不是出在被测应用程序上，而是其他因素。有可能导致测试失败的潜在问题实际上是一个需要解决的真正 bug。我能想到的一个例子是我们系统中的一个 bug，测试在晚上 6:00 通过但在晚上 11:00 失败，这是由于应用程序中的时区 bug 造成的。

## 如何处理不稳定测试？

以一种容易导致测试不稳定的方式构建测试是很容易做到的（即使在我意识到并试图避免的情况下，我也在几个项目中这样做过）。测试数据和状态是我遇到的最大问题，必须在测试自动化项目开始时和整个过程中考虑这些因素。

如果你的主要问题是状态，由于特定的 cookie，Playwright 团队发布了一些新功能来清除某些 cookie，可以在[1.43 版本发布说明](<https://playwrightsolutions.com/a-few-thoughts-on-flakey-tests-playwright-solutions/Building%20your%20tests%20in%20a%20way%20where%20this%20can%20happen%20is%20really%20easy%20to%20do%20/(I've%20done%20it%20on%20a%20few%20projects%20even%20when%20I%20was%20aware%20and%20trying%20not%20to/).%20Test%20Data%20and%20State%20have%20to%20be%20considered%20at%20the%20beginning%20and%20throughout%20building%20automated%20tests.%20If>)中找到。

当你遇到不稳定测试时，要判断这个测试是否仍然有价值。**如果测试没有价值，就删除它！** 如果它有价值，要么修复它，要么将其设置为不频繁运行且不阻塞构建的测试集的一部分。

> 如果测试没有价值，就删除它！

我处理不稳定测试的一种方法是通过 Playwright 标签。我特别使用`@unsatisfactory`作为标签名，因为它让我失望。实际上，在我的日常工作中，我有大约 70 个 API 测试以这种方式分类，我们每周运行一次以获得反馈，但不是在每次构建时运行。使用 Playwright 的`npx playwright test --grep-invert @unsatisfactory`命令，你可以在主 CI 管道中运行所有 spec，除了那些标记为`@unsatisfactory`的。

如果你想实现标签，请查看[1.42 版本发布说明](https://playwright.dev/docs/release-notes#version-142)，了解在测试中创建标签的最新方法。你不再需要在测试标题中添加标签（尽管如果你愿意，仍然可以这样做）。

```typescript
import { test, expect } from "@playwright/test";

test(
  "不稳定测试",
  {
    tag: "@unsatisfactory",
  },
  async ({ page }) => {
    // ...
  }
);

test("稳定测试", async ({ page }) => {
  // ...
});
```

## 我认为的不稳定环境/基础设施

- 第三方服务是否失败？
- 服务/API 调用是否达到了速率限制？
- 测试是否每隔一次运行就通过，因为我们只将最新代码部署到一半的运行服务器上？
- 容器是否因为我们在最便宜的服务器上运行（因为它是测试环境）而崩溃？
- 自动化是否在混沌测试或负载测试期间运行？
- 开发人员是否推送了代码并导致环境重新部署？
- 数据团队是否大量操作数据库以重建他们的数据仓库？
- 你所在地区的 AWS 是否出现故障？

有许多不同的情况可能导致你的环境或基础设施使测试返回"失败"。在这些情况下，与上面的不稳定测试一样，调查每次失败并确定没有真正的问题是至关重要的。不要仅仅做出假设，深入研究失败消息、网络跟踪和基础设施日志/仪表板，以确保测试失败的原因。

我遇到过几次测试开始间歇性失败的情况，第一天我确信这是一个不稳定的基础设施问题，但第二天我决定深入调查。我检查了我们的 pganalyze 工具，它提供了对我们数据库查询的概览，清楚地看到问题是由于一个新查询执行时间是原来的 20 倍。与开发人员合作后，我们为表添加了一个索引，在问题进入生产环境之前就修复了这个 bug！

如果你接受可能有一个 api 或测试会失败，但你仍然想测试并确保它至少能在 X 次中通过 1 次，你可以尝试在测试中使用[expect.poll()](https://playwright.dev/docs/test-assertions#expectpoll)或[expect.toPass()](https://playwright.dev/docs/test-assertions#expecttopass)。我发现使用这些方法的最佳场合是在测试运行之前"创建测试数据"时，因为如果你在实际测试断言步骤中使用它们，可能会掩盖系统的潜在问题。

你还可以通过模拟某些请求和/或响应来使测试更稳定。[Playwright 文档](https://playwright.dev/docs/mock#mock-api-requests)提供了许多好的例子！

## 防止将不稳定测试引入你的项目

理想情况下，你不想将不稳定测试引入你的仓库。防止这种情况的最佳方法是在代码合并到你的测试仓库之前多次运行你的测试。下面的文章将指导你如何循环运行测试，以在合并到主代码分支之前检查不稳定性。

[在 Playwright Test 中是否有一种简单的方法来多次循环测试以检查不稳定性？我发现在合并新代码到测试套件的主分支之前，在拉取请求上多次运行新的自动化测试或对现有测试的编辑是一个很好的做法。](https://playwrightsolutions.com/in-playwright-test-is-there-an-easy-way-to-loop-the-test-multiple-times-to-check-for-flakiness/)

我想我们都同意：

- 酥脆的饼皮 = 好
- 不稳定的测试 = 坏

![图片 3](https://playwrightsolutions.com/content/images/2024/06/Flakey-Test---BAD.png)

## 来源

[原文地址](https://playwrightsolutions.com/a-few-thoughts-on-flakey-tests-playwright-solutions/)

发布时间：2024-06-10
