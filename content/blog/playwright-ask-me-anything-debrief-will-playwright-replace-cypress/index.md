+++
date = 2023-12-18
title = "Playwright 会取代 Cypress 吗?"
description = "不会取代，会共存"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

上周我有幸参加了由 Ministry of Testing 主办的[Playwright 交流活动](https://www.ministryoftesting.com/events/testing-ask-me-anything-on-playwright)。在一小时的活动中,我们收到了大量问题,我认为值得在几篇文章中深入探讨。

今天我计划简要介绍,并回答以下问题:

> Playwright 会取代 Cypress 吗?使用 Playwright 进行 Web 应用自动化测试时,最大的挑战是什么?

## Playwright 会取代 Cypress 吗?

不会的...

为什么呢?过去 5 年里,数以千计的团队已经在项目中采用了 Cypress 作为测试框架。对大多数团队和项目来说,为了获得微小的商业价值而将这些项目转换为 Playwright,成本上并不允许。更有可能的是,团队从切换框架中获得的价值主要是能够并行运行测试,这直接影响开发和质量团队,而不是增加实际的业务价值。在大多数组织中,这样的项目很难获得批准。

只要 Cypress 能提供价值和有用的反馈,我认为它就不会消失。社区已经建立了许多解决方案,包括通过使用`cy.task()`在 Cypress 测试中运行 Playwright/Selenium 的能力。

[增强 Cypress 框架](https://eleks.com/blog/cypress-framework-playwright-selenium-injections/)

## 会有更多的团队在开始新项目时会选择使用 Playwright 吗?

是的,我相信会的!Playwright 相对于 Cypress 的优势在于,它允许我按照自己的意愿在任何地方运行测试,使用任何自定义 reporter,这使得选择 使用 playwright 成了一个非常自然的决定。

对我来说,Cypress.io 还有很多未知因素。我们知道他们曾[募集 4000 万美元 B 轮融资](https://www.prnewswire.com/news-releases/cypressio-raises-40m-in-series-b-to-deliver-the-next-era-of-software-testing-301194275.html),我相信他们正在寻找建立可持续开展业务的方法(写这篇文章时,距离 B 轮融资已经过去 3 年了)。

虽然 Playwright 的亲爹是微软,仍有一些未知因素,微软的项目也是有可能被砍掉的。但当我看到他们为开发者社区构建和提供的工具时,**我会把赌注押在微软身上**。看看 TypeScript、VS Code、.Net Core 等,我对 Playwright 的未来并不太担心。

通常不会...

一般情况下除非工具或者框架进入生命周期的末期，我们通常不用担心它会被砍掉!但是，最近的例子是[Test Project](https://blog.testproject.io/2022/11/17/testproject-end-of-life-your-questions-answered/#:~:text=When%20and%20how%20does%20this,the%20platform%20will%20be%20revoked.)。该团队宣布这个工具不维护了,并提供了将测试用例迁移到他们拥有的其他工具的方法。这个工具最初是一个用于 Web、移动和 API 测试的免费自动化测试平台。

![图片3](https://playwrightsolutions.com/content/images/2023/12/image-4.png)

## 那 Selenium 呢?

我不能不提到老牌的 Selenium。实际上,我认为 Selenium 是一个很棒的项目。它不像 Playwright (TS/JS)和 Cypress.io 那样是一个测试框架,selenium 是一个允许你与 Web 浏览器交互的通用工具。如果你想把它用作测试框架,你需要自带测试框架。

有太多项目已经有了数百甚至上千个测试,出于和第一部分相同的原因,迁移 1000 个正在为组织带来价值的 UI 测试并没有业务价值,因此不应该被优先考虑。

## 你的测试是否提供价值?

我提到的一个重要问题是...你的测试是否为团队提供了价值?无论它们是用什么语言或框架编写的,重要的是它们是否有价值。

如果答案是否定的,那就放弃它们;如果答案是肯定的,那就想办法来维护它们,并继续让它们发光发热。

---

感谢阅读!如果你觉得这篇文章有帮助,请在[LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew)上联系我,或考虑[为我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想获得更多内容直接发送到你的邮箱,请在下方订阅,别忘了留下 ❤️ 表示支持。

## 来源

URL 来源: https://playwrightsolutions.com/playwright-ask-me-anything-debrief-will-playwright-replace-cypress/

发布时间: 2023-12-18T13:30:09.000Z
