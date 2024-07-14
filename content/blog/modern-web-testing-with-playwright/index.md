+++
date = 2023-07-28
title = "使用 Playwright 进行现代网页测试"
description = "了解自动化测试的本质"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

Playwright 是一个出色的新型网页测试框架,它可以帮助你采用现代方法进行网页的测试开发。让我们一起来了解如何使用它。

## 深入思考测试的本质

让我问你一系列问题:

问题 1: 你喜欢代码中出现 bug 吗? 大概率不会。Bug 就是麻烦,它们本不该出现,而且还需要花精力去修复。总之,bug 就是个大麻烦。

问题 2: 你愿意让这些 bug 流入生产环境吗? 当然不愿意! 我们希望在用户看到之前就修复 bug。严重的 bug 可能会对系统、业务甚至声誉造成巨大损害。一旦 bug 不小心溜进了生产环境,我们也要尽快发现并修复。

问题 3: 你喜欢创建测试来提前捕获 bug 吗? 嗯...这个问题就不那么容易回答了。大多数人都明白,好的测试能为软件质量提供宝贵的反馈,但并非每个人都乐意投入精力进行测试。

## 为什么对测试不太感冒?

为什么不是所有人都喜欢测试呢? **因为测试很难!** 以下是我经常听到的抱怨:

- 测试太慢 - 运行时间太长!
- 测试很脆弱 - 应用稍有变动就会失败!
- 测试不稳定 - 经常莫名其妙地崩溃!
- 测试难以理解 - 复杂且难以阅读!
- 测试不创造价值 - 我们应该把时间花在开发新功能上!
- 测试需要切换上下文 - 打断了开发工作流!

![图1: 测试挑战](https://automationpanda.com/wp-content/uploads/2023/07/testing-pain-points-1061611341-e1690484881718.png)

这些都是合理的理由。为了缓解这些痛点,软件团队历来围绕[测试金字塔](https://automationpanda.com/2018/08/01/the-testing-pyramid/)制定测试策略,从上到下将测试分为以下几层:

- UI 测试
- API 测试
- 组件测试
- 单元测试

![图2: 测试金字塔](https://automationpanda.com/wp-content/uploads/2023/07/testing-pyramid-3004920334-e1690484079544.png)

底层测试被认为"更好",因为它们更接近代码,更容易自动化,执行速度更快。它们也被认为不太容易出现不稳定的情况,因此更易于维护。顶层测试则恰恰相反:规模大、速度慢、成本高。金字塔的形状暗示团队应该在金字塔底部的测试上投入更多时间,而在顶部的测试上投入较少时间。

端到端测试其实非常有价值。遗憾的是,测试金字塔将它们标记为"困难"和"糟糕",主要是因为不良实践和工具的局限性。这也导致团队制定的测试策略更强调测试的类别,而不是测试所能提供的结果。

## 重新思考现代网自动化的测试目标

测试不必如此困难,也不必受制于过去的问题。我们应该用全新的方式来测试现代网页应用。

以下是现代网页测试的三个主要目标:

1. 专注于建立**快速反馈循环**,而不是特定类型的测试。
2. 让测试开发变得**尽可能快速和轻松**。
3. 选择能自然**融入开发工作流**的测试工具。

![图3: 现代测试目标](https://automationpanda.com/wp-content/uploads/2023/07/modern-web-testing-goals-2430785089-e1690484965113.png)

这些目标强调了*结果*和*效率*。测试应该成为开发过程中自然而然的一部分,不应产生任何隔阂。

## Playwright 简介

[Playwright](https://playwright.dev/)是一个现代网页测试框架,可以帮助我们实现这些目标。

- 它是微软的一个开源项目。
- 它通过(超快的)调试协议操控浏览器。
- 它支持 Chromium/Chrome/Edge、Firefox 和 WebKit。
- 它提供自动等待、录制回放、UI 调试模式等功能。
- 它可以同时测试 UI 和 API。
- 它为 JavaScript/TypeScript、Python、Java 和 C#提供绑定。

![图4: Playwright概览](https://automationpanda.com/wp-content/uploads/2023/07/playwright-overview-145765983-e1690485021191.png)

Playwright 采用了独特的浏览器自动化方法。首先,它使用浏览器*项目*而不是完整的浏览器应用。例如,这意味着你会测试 Chromium 而不是 Google Chrome。浏览器项目更小,占用的资源也比完整浏览器少。Playwright 还会为你管理浏览器项目,所以你不需要安装额外的东西。

其次,它非常高效地使用浏览器:

1. Playwright 不会为每个测试启动一个全新的浏览器实例,而是为整个测试套件启动一个浏览器*实例*。
2. 然后,它为每个测试从该实例创建一个唯一的*浏览器上下文*。浏览器上下文本质上就像一个隐身模式:它有自己的会话存储和标签页,不与其他上下文共享。浏览器上下文的创建和销毁都非常快。
3. 之后,每个浏览器上下文可以有一个或多个*页面*。所有 Playwright 交互都通过页面进行,比如点击和抓取。大多数测试只需要一个页面。

![图5: Playwright的浏览器、上下文和页面](https://automationpanda.com/wp-content/uploads/2023/07/browsers-contexts-pages-880645586-e1690484653870.png)

Playwright 会自动为你处理所有这些设置。

## Playwright 与其他工具的比较

Playwright 并不是唯一的浏览器自动化工具。其他两个最流行的工具是[Selenium](https://www.selenium.dev/)和[Cypress](https://www.cypress.io/)。以下是一个高层次的比较图表:

![图6: 浏览器自动化工具比较](https://automationpanda.com/wp-content/uploads/2023/07/tool-comparison-3467232613-e1690485288193.png)

这三个都是不错的工具,各有优势。Playwright 的主要优势在于它提供了出色的开发者体验,执行速度最快,支持多种编程语言,并且有几个提高生活质量的特性。

## 学习 Playwright

如果你想学习如何使用 Playwright 进行网页测试自动化,可以尝试我的教程*[使用 Playwright 进行精彩的网页测试](https://github.com/AutomationPanda/awesome-web-testing-playwright)*。所有说明和示例代码都在 GitHub 上。这个教程设计为自学指南,快来试试吧!

Test Automation University 还提供了一个[Playwright 学习路径](https://testautomationu.applitools.com/learningpaths.html?id=playwright-path)

Playwright 是一个出色的现代网页测试框架。快来尝试一下,告诉我你用它自动化了什么!

## 来源

URL 来源: https://automationpanda.com/2023/07/28/modern-web-testing-with-playwright/

发布时间: 2023-07-28T13:00:00+00:00
