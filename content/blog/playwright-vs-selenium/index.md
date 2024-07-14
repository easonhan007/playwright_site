+++
date = 2024-07-11
title = "playwright和selenium的区别"
description = "playwright和selenium的区别是什么？playwright会取代selenium吗？"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础"]
[extra]
math = false
image = "banner.png"
+++

playwright 是微软推出的一款 e2e（端到端）测试工具，支持多种语言及浏览器，那么它会成为下一个 selenium 吗？

我们首先看看 playwright 和 selenium 之间的区别。

## playwright 和 selenium 的区别

Playwright 和 Selenium 都是用于 web 自动化测试的工具,但它们有一些重要的区别。以下是它们的主要对比:

1. 浏览器支持:

   - Playwright: 原生支持 Chromium, Firefox, 和 WebKit。
   - Selenium: 支持更多浏览器,包括 Chrome, Firefox, Safari, IE 等。

2. 架构:

   - Playwright: 使用浏览器特定的协议直接与浏览器通信。
   - Selenium: 使用 WebDriver 协议,需要额外的驱动程序。

3. 性能:

   - Playwright: 通常更快,因为它直接与浏览器通信。
   - Selenium: 可能较慢,因为它通过 WebDriver 进行通信。

4. 自动等待:

   - Playwright: 内置智能等待机制。
   - Selenium: 需要手动实现显式或隐式等待。

5. 多标签页和 iframe 处理:

   - Playwright: 提供更简单的 API 来处理多标签页和 iframe。
   - Selenium: 处理这些场景相对复杂。

6. 移动测试:

   - Playwright: 主要 focused on 桌面浏览器,但可以模拟移动设备。
   - Selenium: 通过 Appium 支持真实移动设备测试。

7. 语言支持:

   - Playwright: 支持 JavaScript, TypeScript, Python, .NET, 和 Java。
   - Selenium: 支持更多语言,包括上述语言以及 Ruby, PHP 等。

8. 社区和生态系统:

   - Playwright: 较新,但发展迅速。
   - Selenium: 历史悠久,有大量的社区支持和插件。

9. 网络拦截和修改:

   - Playwright: 提供强大的内置功能。
   - Selenium: 需要借助第三方工具。

10. 学习曲线:
    - Playwright: 对于新项目来说可能更容易上手。
    - Selenium: 有更多的学习资源,但某些概念可能较复杂。

## Selenium 的成功的原因

selenium 作为浏览器自动化项目来说是非常成功的存在。Selenium 现在已经被下载了几百万次，并继续在全球范围内被广泛接受和使用。

1. Selenium 是开源的，支持多种（如 Java、C#、Js、Python、Ruby、Perl 等），支持所有的浏览器（chrome、firefox、edge、ie、safari、opera 等），可以在多种操作系统（Windows、MAC、Linux）上运行。
2. Selenium 功能强大--它可以做 web 测试，也能做跨浏览器兼容性测试。另外 selenium 设计的初衷是浏览器的自动化，所以除了用作测试之外，selenium 还在 web 自动化操作领域有所建树。
3. Selenium 有一个庞大的用户社区，可以帮助你快速入门。
4. 与其他开源工具相比，Selenium 非常稳定，它的实现甚至成了标准的 w3c 协议。
5. 最后，Selenium 社区是充满活力的，定期举行许多活动和研讨会，你可以与志同道合的人讨论最新的工具和技术。

## playwright 会成为下一个 selenium 吗？

考虑到现代 Web 应用自动化，Selenium WebDriver 似乎是最受欢迎的工具之一，然而，像 Playwright、Puppeteer、Cypress 这样的替代工具正在出现，并争取在一段长时间之后能对其进行超越。

Playwright 是一个 JavaScript 框架，支持在前端实现 Web 应用程序的自动化。它在后端使用 Node.js，就像 Puppeteer 那样。它扩展了该框架，为用户提供了编写端到端测试或隔离测试应用程序特定部分所需的所有工具。

支持使用包括 Java、Js、C#、Python 在内的语言编写测试用例，并像 Selenium WebDriver 一样在任何浏览器和任何操作系统上运行。它是开源的，很容易使用，支持单兵作战和团队协同。

在 UI 自动化领域，Playwright 能够成为下一个 Selenium 的主要原因有以下七个方面。

- Playwright 得到了微软的支持，其作者来自 Puppeteer（谷歌）团队，因此 playwright 可以吸收 Puppeteer 积极的方面。另外，它已经了一些版本来支持多种编程语言，社区的反馈也非常积极。简而言之微软的钞能力和干爹属性使其相对其他开源项目来说可能会有更多的持续性。

- Playwright 的架构更简化，它摆脱了 selenium 复杂的设置和维护本地 driver 的繁琐过程，基本上开箱即用，工程化方面的实践也更加深入。初学 selenium 的同学应该记得 selenium 安装之后没有下载 driver 的话就是不能用的，特定版本的浏览器需要特定版本的 driver 配合，对于一些长期项目的维护来说确实有时候会带来额外的工作量。

- Playwright 的测试执行速度非常高（平均比 selenium 快 40%），因为它使用 JavaScript 引擎如 Node.js 来运行测试，而不是 Selenium 的 driver 程序。因此，与 Selenium WebDriver 相比，使用 Playright 可以大大降低测试执行时间。

- 与 Selenium WebDriver 不同，Playwright 除了支持测试页面的全屏截图外，还支持边测试边录屏，感觉现代化了不少。

- 与 Selenium WebDriver 相比，Playright 的维护成本更低，因为它使用内部等待，而不像 Selenium WebDriver 需要管理显式等待。这大大降低了总的代码编写和维护成本。

- Playwright 除了支持 web 自动化测试外，还支持 RESTFul API 测试。这使测试人员可以灵活地使用 Playwright 测试他们的后端服务。

- 最后，Playwright 可以跟浏览器的开发者工具进行集成，这使得用 Playwright 编写开发测试非常容易和简单。

**总之 playwright 很有潜力成为下一个 selenium，成为开源自动化测试的现象级项目。**

## 那我应该学习 playwright 还是 selenium？

- 如果你时间有限，代码能力有限，那么 playwright 是快速入门的首选;
- 如果你对 ui 自动化测试有着更高的追求和热情，那么两种工具都很值得学习;
- 如果你是 selenium 的忠实用户，那么了解 playwright 也是一个不错的选择和 side project;

总之，如果时间有限就直接 playwright，如果精力有剩余的话，两种工具都非常值得学习。
