+++
date = 2023-11-03
title = "Playwright真实项目里哪些断言使用频率比较高"
description = "Playwright 测试套件中断言的统计, 当我目前的工作项目的测试（测试文件）数量超过一百个时，我开始有兴趣了解哪些断言是最常用的。"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

## 关于测试项目的介绍:

我的测试项目是一个现代的客户端-服务器应用程序。后端（API）单独测试。前端（基于 React）充满了业务逻辑，拥有多模式界面：

![图片 3: UI 设计图](https://miro.medium.com/v2/resize:fit:1000/1*qAP8yJixSvKffSdElE3bBQ.png)

⬆️UI 设计图；[背景图片来源](https://www.esa.int/ESA_Multimedia/Images/2006/12/Location_of_buried_basins_detected_by_MARSIS)

自动化测试覆盖了超过 80%的功能，是回归测试的主要组成部分。

## Playwright 测试套件包括:

- **103 个测试文件；**
- **955 个测试；**
- **601** 个 [expect](https://playwright.dev/docs/api/class-playwrightassertions#playwright-assertions-expect-generic) **方法**（在 97 个测试文件中）；
- 其中有 50 个负向检查（断言在匹配器之前有 `.not`）~ 8.5%的 `expect` 是负向的；
- 页面对象模型中没有断言，但有 **185 个等待定位器的 `awaits`**；
- 在 `beforeAll` 或 `afterAll` 钩子中没有断言（见[自动化测试编写原则第 2 条](https://medium.com/@adequatica/principles-of-writing-automated-tests-a2b72218264c#6da4)）；
- 所有断言都是可执行的（测试中没有 if 语句，见[自动化测试编写原则第 7 条](https://medium.com/@adequatica/principles-of-writing-automated-tests-a2b72218264c#8fbe)）；
- 没有[软断言](https://playwright.dev/docs/test-assertions#soft-assertions)；
- 所有测试在 CI 中以 4 个线程运行，耗时 14 分钟。

我需要一些澄清：我在页面对象中使用 [waitFor()](https://playwright.dev/docs/api/class-locator#locator-wait-for) 方法等待定位器的特定状态，这*可以被视为一种断言*，因为如果定位器不满足条件，测试将失败。这就是为什么有些测试（测试文件）可能没有 [expect](https://playwright.dev/docs/api/class-playwrightassertions) [断言](https://playwright.dev/docs/api/class-playwrightassertions)，因为它们仅包含具有 `waitFor()` 的页面对象，如下所示：

页面对象示例：

```typescript
export class Dungeon {

private gemstone: Locator;

constructor(page: Page) {
 this.gemstone = page.locator('.mineral_crystal');
 }

async waitForGem(visibleState: boolean): Promise<void> {
 await this.gemstone.first().waitFor(state: 'visible');
 }
}
```

测试示例：

```typescript
test("Should have a gem", async () => {
  const dungeon = new Dungeon(page);
  await dungeon.waitForGem(true);
});
```

这就是为什么我将 `waitFor()` 添加到断言的 top 列表中，与[通用断言](https://playwright.dev/docs/api/class-genericassertions)一起。

## top 断言列表:

1.  `.toBe`— 328
2.  `waitFor()` — 185
3.  `.toStrictEqual` — 67
4.  `.toContain` — 54
5.  `.toEqual` — 39
6.  `.toHaveURL` — 34
7.  `.toHaveAttribute` — 22
8.  `.toBeChecked` — 15
9.  `.toHaveClass` — 14
10. `.toBeGreaterThanOrEqual` — 10
11. `.toBeNull` — 6
12. `.toMatch` — 4
13. `.toBeTruthy` — 4
14. `.toBeGreaterThan` — 2
15. `.toBeFalsy` — 2

![图片 4: 断言顶部列表](https://miro.medium.com/v2/resize:fit:1000/1*9rDEfHvlV90Q2hyajQsnDQ.png)

👆top 断言列表: `expect` + `waitFor()`

结果非常令人期待：

- **60%以上** — 检查数据是否有某个值；
- 大约四分之一 — 等待某些东西（定位器/文本）；
- 剩下的 10–15% — URL/标题匹配，罕见的 CSS 属性检查等。

这与我之前参与的项目非常相似。

阅读更多关于 Playwright 断言的信息：[断言](https://playwright.dev/docs/test-assertions)。

## 来源

[URL Source](https://adequatica.medium.com/statistics-of-assertions-in-playwright-test-suite-9e464866982d)

发布日期: 2023-11-03
