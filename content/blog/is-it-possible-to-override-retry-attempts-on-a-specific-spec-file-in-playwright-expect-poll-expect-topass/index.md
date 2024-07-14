+++
date = 2023-08-07
title = "Playwright 中能否对特定的 spec 文件设置重试次数"
description = "可以，但用poll和pass断言会更优雅"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

这个问题最近在 Playwright Discord 的 #help-playwright 频道中被提出。如果你还没加入,现在就[加入吧](https://discord.gg/playwright-807756831384403968)!

今天的解决方案我将使用 [https://practicesoftwaretesting.com/](https://practicesoftwaretesting.com/#/) 网站作为测试对象。源码的 pull request 可以在下面的链接找到。

主要涉及的主题包括 `test.describe.configure({ retries: x })`, `expect.poll()`, 和 `expect.toPass()`

[Adding Retry Count Logic By Spec by BMayhew](https://github.com/playwrightsolutions/playwright-practicesoftwaretesting.com/pull/2)

在深入了解具体解决方案之前,我认为值得问问自己:为什么测试套件中需要重试?许多人会认为,不应该在测试套件中重试,而应该要研究每次失败的用例,要么修复存在的 bug,要么改进不稳定的测试以使其更加稳定。

但实际上,这并非总是可行,具体取决于你的环境。在我目前的环境中,我们确实依赖重试来帮助我们获得正确的结果。这是我们做出的选择和愿意承担风险,对套件中的每个测试进行最多 2 次重试。我们通常会定期审查重试情况,研究测试最初失败的原因,并努力修复测试的逻辑问题。在我的环境中,大多数情况下,不稳定性更多来自于我们在"临时"和"预发布"环境中的机器规格问题。我遇到的许多错误恰好是服务器 502、503,即服务器响应时间过长。对我们来说,这些环境比生产环境小,并不总能优雅地处理我们的自动化测试所产生的所有流量。我发现我们的测试并不是不稳定的,而是我们的机器规格和基础设施不稳定。

话虽如此,我们的自动化检查实际上帮助我们识别了一个负载均衡器计时问题(在 TCP/IP 级别),这是由大量的失败而引起的,重新运行后就通过了。我们在深入研究"重试"的测试用例并与 SRE 团队一起回顾后,才发现了应用程序会话超时和负载均衡器健康检查超时之间的配置错误。

说完这些,让我们进入解决方案吧!

## test.describe.configure({ retries: x })

在 `playwright.config.ts` 文件中,我将重试次数设置为 `2`。在特定的测试文件中,我可以在文件开头(在任何 `test.describe()` 或 `test()` 块之外)使用 `test.describe.configure()` 来覆盖重试次数。以下代码将把该文件中的所有测试设置为重试 5 次。这是一种非常直接的方法,但还有其他方法!

```javascript
import { test, expect } from "@playwright/test";

test.describe.configure({ retries: 5 });

test.describe("测试重试 ", () => {
  test.use({ storageState: ".auth/customer01.json" });

  test("使用有效的客户凭据登录并验证品牌页面不可访问", async ({ page }) => {
    await page.goto("/");

    expect(await page.getByTestId("nav-user-menu").innerText()).toContain(
      "Jane Doe"
    );
    await page.goto("/#/admin/brands");
    await expect(page.getByTestId("email")).toBeVisible();
    await expect(page.url()).toContain("/#/auth/login1");
  });
});
```

[官方文档里的描述](https://playwright.dev/docs/test-retries#retries)

值得一提的是,你可以通过在 Playwright 测试中使用 `expect.poll()` 或 `expect.toPass()` 功能来解决许多与测试重试相同的问题。让我们看看下面每种方法的例子。

## expect.poll()

expect.poll() 是一个很有用的工具，它可以让我们重复检查某个条件是否满足，直到成功或超时。想象你在等一个网页加载，但不知道具体要多久。你可能会不断刷新页面，直到看到你想要的内容。expect.poll() 就是在自动帮你做这件事。

在下面的例子中，我们设置了 20 秒的等待时间。代码会不断尝试，看是否能找到包含 "/#/auth/login1" 的内容。如果找到了，就立即停止；如果 20 秒内都没找到，就会报告失败。

这个方法特别适合处理那些需要一定时间才能完成的操作。比如，在我的一个项目中，我们首先让浏览器打开一个网页，然后等待它可能发生的跳转。我们不断检查当前的网址，直到它变成我们期望的地址。这样，即使网页经过了几次跳转，我们最终也能确认它到达了正确的位置。

不过要注意，如果在这个等待过程中，我们设置的任何检查条件失败了（比如找不到某个元素），整个测试就会立即失败，不会继续等待了。

```javascript
import { test, expect } from "@playwright/test";

test.describe("测试轮询 ", () => {
  test.use({ storageState: ".auth/customer01.json" });

  test("使用有效的客户凭据登录并验证品牌页面不可访问", async ({ page }) => {
    await page.goto("/");

    expect(await page.getByTestId("nav-user-menu").innerText()).toContain(
      "Jane Doe"
    );

    await expect
      .poll(
        async () => {
          await page.goto("/#/admin/brands");

          // 如果下面的断言失败,测试就失败
          await expect(page.getByTestId("email")).toBeVisible();

          return page.url();
        },
        {
          timeout: 20_000,
        }
      )
      .toContain("/#/auth/login");
  });
});
```

[官方文档的描述](https://playwright.dev/docs/test-assertions#expectpoll)

## expect.toPass()

`toPass()` 方法和前面说的轮询方法很像，但它有个很重要的不同点。想象你在做一道复杂的数学题，里面有好几个步骤。

- 使用 `expect.poll()` 就像你在检查最后一个步骤是否正确。如果最后一步错了，整个题就算做错了。

- 而使用 `toPass()` 就像老师给你多次机会重做整道题。如果任何一个步骤做错了，你就要从头再来，直到所有步骤都做对，或者直到用完了所有的重做机会（也就是到达了设定的超时时间）。

具体到代码中：

- 在 `await expect(async()....` 这个代码块里，可能有多个检查点（就像数学题的多个步骤）。
- 如果其中任何一个检查失败了，`toPass()` 会让整个代码块重新运行，从头再来。
- 这个过程会一直重复，直到所有的检查都通过，或者超过了设定的时间限制。

这就是 `expect.poll()` 和 `expect.toPass()` 最大的区别：`toPass()` 在失败时会重试整个过程，而不仅仅是最后一步。这对于处理那些需要多个步骤都成功的复杂操作特别有用。

```javascript
import { test, expect } from "@playwright/test";

test.describe("测试 toPass ", () => {
  test.use({ storageState: ".auth/customer01.json" });

  test("使用有效的客户凭据登录并验证品牌页面不可访问", async ({ page }) => {
    await expect(async () => {
      await page.goto("/");

      expect(await page.getByTestId("nav-user-menu").innerText()).toContain(
        "Jane Doe"
      );
      await page.goto("/#/admin/brands");

      // 如果下面的断言失败,整个块将被重试
      await expect(page.getByTestId("email")).toBeVisible();

      await expect(page.url()).toContain("/#/auth/login");
    }).toPass({
      timeout: 10_000,
    });
  });
});
```

[官方文档](https://playwright.dev/docs/test-assertions#expecttopass)

反复运行测试而不分析原因是很危险的。想象一下，你在做一道难题，一直得不到正确答案。如果你只是不停地重做，而不去思考为什么错了，可能永远也解不开这道题。

我们进行自动化测试的真正目的是什么呢？就像是给开发团队一个"安全网"。每次他们修改代码后，我们都要确保：

1. 新的改动没有把原本正常工作的功能弄坏。
2. 整个应用程序仍然运行良好，没有变得更糟糕。

如果测试能稳定地通过，它就像是给了我们一个"绿灯"，让我们有信心说："好的，这次的改动没问题，我们可以放心地把新版本发布出去了。"

所以，与其盲目地重复测试，不如仔细分析每次失败的原因，这样才能真正提高软件的质量和可靠性。

![图片 9](https://playwrightsolutions.com/content/images/2023/08/image.png)

---

感谢阅读!如果你觉得这篇文章有帮助,请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上联系我,或考虑[给我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想在收件箱中收到更多内容,请在下方订阅,别忘了留下一个 ❤️ 表示你的喜爱。

## 来源

URL 来源: https://playwrightsolutions.com/is-it-possible-to-override-retry-attempts-on-a-specific-spec-file-in-playwright-expect-poll-expect-topass/

发布时间: 2023-08-07
