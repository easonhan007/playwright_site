+++
date = 2024-07-24
title = "为什么page.goto()会拖慢你的playwright测试脚本"
description = "省流：因为默认等待策略会等待所有的资源加载完毕"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在使用Playwright进行端到端测试时，您面临着一个两难的局面。一方面，测试的稳定性至关重要。毕竟，没有什么比一个反复无常的测试套件更让人头疼的了。另一方面，测试的执行速度同样不容忽视。试想一下，当您急需部署一个紧急的生产环境修复时，却不得不干等几个小时才能看到测试结果，这种感觉恐怕会让人抓狂。

那么，当您听说page.goto()这个常用指令可能正是拖慢测试速度的元凶时，您会作何感想？这个问题值得我们深思。

准备好一起探讨如何在保证稳定性的同时提升测试效率了吗？让我们开始这段有趣的旅程吧！

## 每个Playwright脚本的开始 — page.goto()

这里有一个非常基础的Playwright脚本。

```javascript
login.spec.js
import { expect, test } from "@playwright/test";

test("Login works", async ({ page }) => {
  await page.goto("/");

  const loginLink = page.getByRole("link", { name: "Login" });
  await loginLink.click();

  const loginHeader = page.getByRole("heading", { name: "Login" });
  await expect(loginHeader).toBeVisible();

  // More things to check after the login link was clicked
  // ...
});
```

它导航到在playwright.config中定义的baseURL的根目录。定位一个链接，点击它，然后测试网站的UI是否相应更新（我隐藏了大部分动作和断言，因为它们对这篇文章不重要）。

这一切运行得很好，我相信您以前也写过类似的Playwright代码。如果您检查您的测试及其持续时间，您可能已经发现page.goto()的执行时间可能会有很大差异。

让我给您展示一个例子。

![Playwright跟踪查看器突出显示缓慢的page.goto调用](https://images.prismic.io/checklyhq/Zo5o0B5LeNNTw_Lp_slow-page-goto.jpg?auto=format,compress)

让我们仔细看看这个Playwright的跟踪记录。令人惊讶的是，page.goto()竟然耗费了整整10秒钟！更有趣的是，从跟踪查看器顶部的预览界面可以看出，在这漫长的等待过程中，示例网站其实一直都是可用状态。

要知道，这还只是一个本地运行的、超级快速的电子商务网站的简单测试用例。想象一下，如果我们要测试一个中等规模商店的所有核心功能，很可能就需要运行上百个测试。这样一来，每个测试中的这点小延迟累积起来，就可能在您的CI/CD流水线中增加超过15分钟的等待时间！

（当然，您可以通过并行运行测试来缩短总体等待时间，但这并不能改变每个测试都被不必要地拖慢的事实。）

那么问题来了，在这段时间里，我们到底在等待什么呢？这个问题值得我们深入探讨。

## page.goto()和load事件

如果您查看Playwright文档，您会发现默认情况下，page.goto()等待load事件。

```javascript
await page.goto("/");

// is the same as

await page.goto("/", {waitUntil: "load"});
```

load事件是什么？MDN是这样说的。

> load事件在整个页面加载完成时触发，包括所有依赖资源，如css、javascript、iframe和图像。

让我们仔细思考一下。每当您调用page.goto()时，您都在等待所有css文件、js脚本、iframe和图像加载完成。总之，您在等待所有内容(!)加载完成后才运行您的测试。

我在复盘上面无脑等待的用例时，我发现网站上某个SVG图像的加载延迟了所有的测试行为。为什么这个文件如此缓慢？我不知道，但资源加载时间较长的可能性总是存在。

![Playwright跟踪查看器突出显示一个加载时间为10秒的logo.svg文件。](https://images.prismic.io/checklyhq/Zo5qnB5LeNNTw_M5_logo-svg-10-seconds.jpg?auto=format,compress)

现在，这只是一个小型演示应用。考虑一个成熟的电商站点；那里将有数百个图像，更不用说所有来自"某处"的js脚本了。对于这样的网站，page.goto()的默认配置将等待所有资源通过网络加载完成之后才点击第一个按钮。这是最好的方式吗？

## 您的用户不会等待所有的http请求 — 为什么您的测试要等呢？

让我们换个角度思考这个问题...

为什么我们要使用真实浏览器进行端到端测试和网站监控呢？显然，我们的首要目标是确保网站和基础设施运行正常。但更重要的是，我们希望通过模拟真实用户的行为来实现这一目标。毕竟，这才是端到端测试的真正意义所在，不是吗？

想象一下，您的普通用户会等待浏览器地址栏上的加载图标完全消失后才开始点击页面元素吗？恐怕不会。我敢打赌，大多数访客看到"加入购物车"按钮的那一刻就会迫不及待地点击，根本不会关心网站是否已经完全加载完毕。人们的行为往往是看到什么就点什么，立即与网站进行互动。

这就是为什么在编写Playwright脚本时，我们应该尽可能地模仟这种自然的人类行为。毕竟，我们的测试越接近真实用户的操作，就越能发现实际环境中可能出现的问题。

那么，回到我们的问题：在测试用例中，我们应该如何更好地模拟用户访问页面的行为呢？这个问题值得我们深入思考，因为它可能是提高测试效率和真实性的关键。

page.goto()的等待行为可以通过waitUntil属性进行配置。您可以定义四种waitUntil设置。

```javascript
// Wait until the HTML starts loading.
await page.goto("/", {waitUntil: "commit"});

// Wait until the HTML is parsed
// and deferred scripts (`<script deferred>` and `<script type="module">`) are loaded.
await page.goto("/", {waitUntil: "domcontentloaded"});

// Wait until all initially included resources are loaded.
await page.goto("/", {waitUntil: "load"});

// Wait until every resource is loaded and the network is silent for 500ms.
await page.goto("/", {waitUntil: "networkidle"});
```

当您查看这些waitUntil选项时，除了commit之外的所有选项都严重依赖网络和资源的加载。这意味着除了commit之外的所有选项都依赖网页上的具体资源，当一个请求卡在网络层时可能会拖慢您的测试速度。

这些选项在速度上有哪些差异？以下是我的示例测试用例的结果。

| "waitUntil" 选项 | "page.goto" 执行时间 |
|-------------------|----------------------|
| commit            | 62ms                 |
| domcontentloaded  | 159ms                |
| load              | 10.1s                |
| networkidle       | 12.6s                |

当然，这些数据是我从本地测试站点上搜集到的。但绝对值并不重要。重要的是看waitUntil选项之间的差异。

不出所料，commit等待选项是最快的goto()配置，因为它除了初始HTML的第一个字节外不等待任何与资源相关的内容。networkIdle是迄今为止最慢的，因为它等待每个资源加载完成，再等500ms。

但这里有一件有趣的事情：无论waitUntil选项如何，所有这些测试都成功了。这个简单的测试用例的总体测试持续时间从大约10秒到25秒不等，但测试结果都是绿色的。

这是怎么回事，它是如何工作的？

## 编写不依赖网络的快速测试

如果您要测试的网站本身就不稳定，那么想要创建稳定和快速的测试用例集合几乎是不可能的。就像俗话说的，巧妇难为无米之炊 — 不稳定的应用程序注定难以产生可靠的测试。

此外，如果您的网站用户体验糟糕，或者采用了不良的[Hydration Patterns](https://playwright.dev/docs/navigations#hydration)，您的测试就不得不使用各种变通方法来勉强通过最基本的功能测试。当然，最理想的做法是直接修复这些应用程序问题，但我们都知道，现实中这往往不太容易做到。

另一方面，如果您在编写Playwright脚本时没有站在用户的角度思考，那么您同样可能会导致测试的不稳定。要想加快测试速度并提高其稳定性，最好的方法是利用自动等待机制和Web优先断言，让Playwright自己去处理其他细节问题。

文章开头的示例脚本中包含了一个看似"简单"的click()指令。实际上，这个click()指令是您的得力助手，因为它背后蕴含着一系列神奇的可操作性检查。

```javascript
// this click() will wait for the login to be
// - visible
// - stable, as in not animating or completed animation
// - able to receives events as in not obscured by other elements
// - enabled
await loginLink.click();
```

每次您使用click()、fill()或其他操作指令时，Playwright都会智能等待，直到目标元素完全就绪，能够响应用户操作。这意味着元素已经完成渲染，变得可见且稳定，并且处于可用状态。

如果您的应用程序设计良好，能够快速呈现出可交互的界面元素，Playwright就能以最快的速度与这些元素进行交互。在这种情况下，您根本不需要额外等待任何网络请求完成。

类似地，当您使用Web优先的断言方式时，Playwright会自动等待，直到用户界面达到您预期的状态。这样一来，您就不必再专门去等待某个特定UI状态背后的HTML加载或API调用完成。

这种方法不仅简化了测试流程，还能更好地模拟真实用户的操作行为，从而提高测试的有效性和可靠性。

```javascript
// wait until this element is visible
await expect(loginHeader).toBeVisible();
```
如果您能够充分利用这两个Playwright的核心原则，您就可以不再过分关注网络层的细节，而是将注意力集中在真正重要的方面 — 用户界面的交互操作及其导致的状态变化。这种方法几乎消除了手动等待网络事件和请求的需求，让您的测试更加高效和可靠。

```javascript
login.spec.js
import { expect, test } from "@playwright/test";

test("Login works", async ({ page }) => {
  // don't wait for all the resources to be loaded
  await page.goto("/", {waitUntil: "commit"});

  // let Playwright wait for this link to be visible
  const loginLink = page.getByRole("link", { name: "Login" });
  await loginLink.click();

  const loginHeader = page.getByRole("heading", { name: "Login" });
  await expect(loginHeader).toBeVisible();

  // More things to check after the login link was clicked
  // ...
});
```

让我们再看看调整后的脚本。我们不再傻等网络事件，而是聪明地等待UI状态变化。Playwright会耐心等到"Login"链接出现，然后立即点击。这个小小的改动让我们的测试速度提升了10秒，同时还能完整覆盖核心登录功能。这不就是双赢吗？

## 但是...世事总有例外

话说回来，在某些情况下，关注网络状况确实很有必要。

在进行端到端测试时，我们经常会在预发布环境上进行测试，以防止核心功能出现回归。理想情况下，预发布环境应该是生产环境的完美复制品。但现实往往不尽如人意。预发布环境通常部署在不同的基础设施上，前端也常常会加载不同的资源来进行跟踪、用户交互和监控。

这些差异有时是可以接受的，毕竟您的主要目的是测试新功能并避免回归。然而，当您将Playwright用于网站监控时，密切关注所有加载的资源就显得尤为重要，这可以帮您及时发现潜在的生产问题。我亲眼见过不止一次，第三方脚本导致生产环境崩溃的情况。

举个例子，我们在Checkly使用Playwright监控checklyhq.com。和大多数营销网站一样，我们也集成了Intercom和各种分析工具。有一天，我们所有的Playwright线上检查突然全部失败了。原因是Intercom在预期时间内没能加载完成。page.goto()的执行时间超过了一分钟，就因为一个JavaScript片段超时了。

那么，checklyhq.com是不是真的出问题了呢？其实没有，网站的核心功能一切正常。但是，及时发现Intercom出现问题难道不是件好事吗？当然是！

通过监控网络层，您可以获得关于网站整体健康状况和性能的宝贵信息。这些洞察可以帮助您更全面地了解您的网站运行情况，及时发现并解决潜在问题。

```javascript
// fail when all resources aren't loaded after 10 seconds
await page.goto("/", { waitUntil: "load", timeout: 10_000 });
```

## 总结

那么，您是否应该立即将所有的page.goto()操作改为commit或domcontentloaded，以在CI/CD中节省时间呢？答案并不是简单的是或否，而是要"具体情况具体分析"。

如果您特别看重测试的执行速度，需要运行大量测试，并且采用了以用户为中心、具有自动等待功能的测试方法，那么不等待所有资源加载确实能为您节省可观的时间 — 可能是几分钟，甚至几小时。不妨试一试，您会发现Playwright在判断何时点击以及点击什么方面相当智能。

不过，请记住，仅仅看到预览部署的绿灯并不意味着万事大吉。真正重要的是确保生产环境的稳定运行。要做到这一点，持续测试您的线上产品是必不可少的。这正是合成监控大显身手的地方。

在使用Playwright进行网站测试和监控时，密切关注那些加载缓慢的网络依赖可能会带来意想不到的收益。一旦您的基础设施、第三方资源或应用程序代码出现问题，您将能第一时间察觉。这才是让您晚上安心入睡的真正保障。

当然，最终如何取舍，还是需要您根据自身情况来决定。

如果您有任何疑问或想法，欢迎来Checkly社区和我们交流。我可以向您保证，我们是一群热情友好的伙伴，随时欢迎您的加入！


## 来源

[原文地址](https://www.checklyhq.com/blog/why-page-goto-is-slowing-down-your-playwright-test/)

发布时间：2024-07-24
