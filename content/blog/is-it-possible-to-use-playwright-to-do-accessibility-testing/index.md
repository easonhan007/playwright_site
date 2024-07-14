+++
date = 2022-10-16
title = "是否可以使用 Playwright 进行无障碍测试？"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

Markdown 内容：

当然可以！Deque 实验室提供了一个名为 axe 的工具来协助这项工作。对于 Playwright，他们专门提供了 axe-core/playwright 包，使用起来比以往更加简单。

以下代码片段展示了如何使用 axe-core/playwright 包中的 `AxeBuilder` 功能。调用 `analyze()` 将返回一个 promise，可以通过等待获取扫描的所有详细信息。我还列举了几种处理结果的方法：在控制台打印结果、将违规情况附加到使用 Playwright 测试运行器生成的测试报告中，以及使用 expect 语句在不符合规范时使测试失败。

```javascript
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
test("Visit home page and run an axe test @axe", async ({ page }, testInfo) => {
  await page.goto("https://broken-workshop.dequelabs.com/");
  //使用 axe 分析页面
  const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
  //将违规情况附加到测试报告
  await testInfo.attach("accessibility-scan-results", {
    body: JSON.stringify(accessibilityScanResults.violations, null, 2),
    contentType: "application/json",
  });
  //在控制台输出违规情况
  let violation = accessibilityScanResults.violations;
  violation.forEach(function (entry) {
    console.log(entry.impact + " " + entry.description);
  });
  //期望违规列表为空
  expect(accessibilityScanResults.violations).toEqual([]);
});
```

上面的示例虽然简单，但查看 Playwright 文档，你会发现更多功能，例如：

- 配置 axe 扫描页面的特定部分
- 从扫描中排除单个元素
- 禁用单个扫描规则（完整的 Axe 规则列表请参见此处）
- 使用快照允许特定已知问题
- 为 AxeBuilder 创建 fixture 以简化代码

你还可以根据想要运行的测试类型，使用特定标签调用 AxeBuilder 进行检查。

```javascript
//使用 axe 分析页面
const accessibilityScanResults = await new AxeBuilder({ page })
  .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
  .analyze();
```

Axe 是一个在多种自动化解决方案中使用的工具，如果你想尝试它的 Chrome 扩展版本，可以在这里安装。

我越是使用和探索 Playwright，就越被它的功能所折服。

[无障碍测试](https://playwright.dev/docs/accessibility-testing)

## 来源

网址来源：https://playwrightsolutions.com/is-it-possible-to-use-playwright-to-do-accessibility-testing/

发布时间：2022-10-16
