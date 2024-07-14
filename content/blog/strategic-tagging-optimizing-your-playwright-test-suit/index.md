+++
date = 2024-03-18
title = "如何用标签来优化你的 Playwright 测试套件"
description = "你是否发现自己每次都在运行完整的自动化测试套件?利用标签(tags)可以精准过滤一部分用例来加速这一过程。"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

你是否发现自己每次都在运行完整的自动化测试套件?利用标签(tags)可以精准过滤一部分用例来加速这一过程。

随着软件项目的发展和自动化项目的扩展,测试数量通常会随着新功能的引入而增加。此时,只运行某些测试的子集变得非常有用。尽管 Playwright 允许测试并行运行,但将测试分割成更小的组别在某些时候会更有益。虽然维护一个强大的自动化测试套件对产品质量至关重要,但不谨慎的测试自动化可能会显著降低团队的进度。一个有效的策略是通过标签来分类你的自动化测试,并在软件开发过程的不同阶段只执行完整测试套件的一个子集。

**考虑以下示例:**

◾ 在非工作时间运行整个测试套件而不打扰团队,并在 pull request 上有选择地运行测试子集,以保持 **CI 流水线** 的速度和效率。  
◾ 允许特定团队(如 QA 或功能团队)只运行他们负责的测试。  
◾ 在生产发布期间运行只涉及读取操作(没有写入操作)的冒烟测试。

标签用于在 HTML 报告、UI 模式或 VSCode 扩展中过滤测试。

使用标签系统允许你将测试分类为逻辑集合。标签使用测试描述中的 **@tag** 语法定义。虽然技术上任何字符串都可以作为标签,但文档更倾向于使用 **@tag** 语法,所以建议遵循这个规则。

**如何安装 Playwright?**

npm init playwright@latest

更多详细信息请访问官方 [Installation | Playwright](https://playwright.dev/docs/intro) 文档。

**如何运行 Playwright 测试?**

```bash
npx playwright test
```

**旧的 Playwright 语法:**

过去,标签被整合到测试标题中,这仍然是一种受支持的方法。然而,这种方法会导致 HTML 报告不好看。Playwright 会自动从标题中提取标签并将其显示为标签,以提高可见性,从而消除了在标题内进行冗余标签的需求。

```typescript
test("Playwright Landing page - Has title @Smoke", async ({ page }) => {
  await page.goto("https://playwright.dev/");
  await expect(page).toHaveTitle(/Playwright/);
});
```

**如何按标签运行测试?**

```
npx playwright test --grep @Smoke
```

![图片 4](https://miro.medium.com/v2/resize:fit:700/1*sh8nQ1APLG4vq_0T7DshFw.png)

👆 旧的 Playwright 标签语法示例

**新的 Playwright 语法:**

根据官方文档所述,引入新的标签语法的原因源于先前语法在 HTML 报告中显得有些冗余，而且也看不太出来。正如我们在旧的 Playwright 语法部分所展示的那样。这种标签方式可能导致混淆和显著的重复,尤其是在处理大量标签时。

要采用新语法,只需生成一个包含标签的数组或单个标签的标签对象:

```typescript
test(
  "Playwright Landing page - Has title",
  { tag: ["@Smoke", "@UI"] },
  async ({ page }) => {
    await page.goto("https://playwright.dev/");
    await expect(page).toHaveTitle(/Playwright/);
  }
);
```

![图片 5](https://miro.medium.com/v2/resize:fit:700/1*ldDx5Z4uAqPunnQ9ZzFJHw.png)

👆 新的 Playwright 标签语法示例

从新语法可以看出,标签不再显示在测试名称内,从而显著提高了可读性。

标签也适用于 describe 语法块:

```typescript
test.describe("Group Example", { tag: "@Group" }, () => {
  test(
    "Playwright Landing page - Has title",
    { tag: ["@Smoke", "@UI"] },
    async ({ page }) => {
      await page.goto("https://playwright.dev/");
      await expect(page).toHaveTitle(/Playwright/);
    }
  );

  test(
    "Playwright Github",
    { tag: ["@Smoke", "@UI", "@Fast"] },
    async ({ page }) => {
      await page.goto("https://github.com/microsoft/playwright");
    }
  );
});
```

![图片 6](https://miro.medium.com/v2/resize:fit:700/1*Ry1DaYod_eLcC-HfEP9aKw.png)

⬆️ Describe 块标签语法示例

使用以下命令将 Playwright 更新到最新版本:

```bash
npm install -D @playwright/test@latest
```

同时下载新的浏览器二进制文件及其依赖项:

```bash
npx playwright install --with-deps
```

要验证你机器上安装的版本,请使用以下命令:

```bash
npx playwright --version
```

## 在测试管理中使用 @tag 的优势:

**简化测试用例管理:** **@tag** 通过对测试用例进行分类来简化测试管理。这种分类允许根据标签快速过滤和识别相关的测试用例。你可以轻松根据特定标签执行的具体的测试用例。

**标签统计热图:** 分析仪表板上提供的标签统计热图提供了有价值的总览。它允许你跟踪与标签相关的指标,如标签总数和带有特定标签的测试用例数量。然而,跟踪按标签划分的测试自动化覆盖率也很重要。

**自定义测试场景:** 你可以灵活地为任何自定义测试场景定义有用的标签。这允许来自不同功能、测试套件或功能文件(BDD)的场景一起执行。例如,你可以执行所有标签为 **@Smoke** 的测试,同时排除那些标签为 **@Regression** 的测试。

## 一些具体的分类示例

**冒烟测试** 是一种在软件构建完成后执行的软件测试技术,用于验证软件的关键功能是否正常工作。它在执行任何详细的功能或回归测试之前进行。冒烟测试的主要目的是拒绝存在错误的软件应用,以便 QA 工程团队不会浪费时间测试一个有问题的软件应用。

**健全性测试** 是一种在收到软件的中间版本后执行的软件测试类型,通常涉及对代码或功能的微小更改。其目的是确保错误已被修复,并且这些更改没有引入新的问题。目标是验证预期的功能大致按预期工作。如果正确性测试给出错误结果,构建将被拒绝,以避免在更广泛的测试上花费时间和资源。

**回归测试** 是在代码更新后进行的一种软件测试,以确保更新没有引入新的错误。这是因为新代码可能带来与现有代码冲突的新逻辑,导致缺陷。通常,QA 团队会为重要功能准备一系列回归测试用例,每次发生这些代码更改时都会重新执行这些用例,以节省时间并最大化测试效率。

![图片 7](https://miro.medium.com/v2/resize:fit:553/1*hirQV3d8tQpEWEuZq-wiCQ.png)

因此,组织好你的测试标签策略非常重要。当你想只运行特定的测试集而不是整个套件时,你就处于更有利的位置。在 Smoke 标签名下,你可以只运行冒烟测试,或者单独运行回归测试。

## 来源

[URL 来源](https://medium.com/@merisstupar11/strategic-tagging-optimizing-your-playwright-test-suit-4ab109343fed)

发布时间: 2024-03-18
