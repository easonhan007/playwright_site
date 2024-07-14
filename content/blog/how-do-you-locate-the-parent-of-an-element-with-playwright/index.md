+++
date = 2023-02-13
title = "如何使用 Playwright 定位元素的父级?"
description = "省流: 最推荐的做法是使用locator以及filter"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

本文将介绍 5 种定位父级元素的方法!

UI 自动化测试中的一个常见挑战是,如何访问或控制网页上没有唯一标识符的元素。以下面的[Challenging DOM](https://the-internet.herokuapp.com/challenging_dom)页面为例,定位编辑按钮并不是一件轻松的任务。页面上有至少 10 个不同的编辑按钮,我们不能仅仅简单的点击带有"edit"文本的链接。

![图片 1](https://playwrightsolutions.com/content/images/2023/02/image-4.png)

首先,我们需要在页面上找到一个可以交互的、在 DOM 中保持一致的唯一标识。在典型的 UI 测试中,当你需要验证表格或网格中的数据时,其父元素通常会有某种唯一标识符。在本例中,我将使用"Adipisci5"作为唯一标识符。我将演示几种不同的方法来与包含"Adipisci5"的行中的 edit 按钮进行交互。以下是页面上 HTML 的截图。

![图片 2](https://playwrightsolutions.com/content/images/2023/02/image-5.png)

我们的目标是找到包含文本"Adipisci5"的数据单元格<td>,然后找到完整的行(如上图高亮显示),最后点击编辑链接。接下来,我将展示几种不同的方法来获取父级行<tr>。

---

## 使用 Playwright locator 的 has 选项

第一个例子使用了 locator 类的 `has` 选项。

```javascript
const row = page.locator("tr", { has: page.locator('text="Adipisci5"') });
```

[locator](https://playwright.dev/docs/api/class-page#page-locator)

## CSS: 通过文本匹配

这个例子利用了 Playwright 内置的 CSS 文本匹配功能。

```javascript
const row = page.locator('css=tr:has-text("Adipisci5")');
```

[Other Locators](https://playwright.dev/docs/other-locators#css-matching-by-text)

### 使用 getByRole 和 accessible name

这个例子使用了新发布的 getByRole 方法,通过 name 选项来查找唯一标识符。

```javascript
const row = page.getByRole("row", { name: "Adipisci5" });
```

[getByRole](https://playwright.dev/docs/api/class-page#page-get-by-role)

## 使用 getByRole 和 filter() 方法

这是一种类似上面的方法,但我们使用了 .filter() 方法,它非常强大,因为你还可以在 hasText 部分使用正则表达式(参见第二个例子)。

```javascript
const row = page.getByRole("row").filter({ hasText: "Adipisci5" });
const row = page.getByRole("row").filter({ hasText: /Adi.*ci5/ });
```

[Filter](https://playwright.dev/docs/locators#filtering-locators)

## 使用 xpath locator("..")

这种方法可行,而且是获取父元素的一种快速方法。总的来说,我不太喜欢在代码中使用 xpath,但这是我唯一允许使用的 xpath 场景。

```javascript
const row = page.locator("text=Adipisci5").locator("xpath=..");
```

![图片 11](https://playwrightsolutions.com/content/images/2023/02/xpath.png)

[other locators](https://playwright.dev/docs/other-locators#parent-element-locator)

下面是一个完整的例子,展示了使用不同方法访问父元素,然后用这些父元素来点击选定行中的编辑链接,并通过对 URL 来断言来确认编辑按钮被点击。

```javascript
import { test, expect } from "@playwright/test";

test.describe("Challenging DOM", async () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("https://the-internet.herokuapp.com/challenging_dom");
  });

  test("使用 Playwright locator 的 has 选项查找父元素", async ({ page }) => {
    await page
      .locator("tr", { has: page.locator('text="Adipisci5"') })
      .getByRole("link", { name: "edit" })
      .click();

    await expect(page).toHaveURL(/.*#edit/);
  });

  test("使用 has-text 查找父元素", async ({ page }) => {
    await page
      .locator('css=tr:has-text("Adipisci5")')
      .locator("text=edit")
      .click();

    await expect(page).toHaveURL(/.*#edit/);
  });

  test("使用 getByRole locator 和 accessible name 查找父元素", async ({
    page,
  }) => {
    await page
      .getByRole("row", { name: "Adipisci5" })
      .getByRole("link", { name: "edit" })
      .click();

    await expect(page).toHaveURL(/.*#edit/);
  });

  test("使用 getByRole locator 和带正则表达式的 filter 查找父元素", async ({
    page,
  }) => {
    await page
      .getByRole("row")
      .filter({ hasText: /Ad.*sci5/ })
      .getByRole("link", { name: "edit" })
      .click();

    await expect(page).toHaveURL(/.*#edit/);
  });

  test("使用 xpath 查找父元素", async ({ page }) => {
    await page
      .locator("text=Adipisci5")
      .locator("..")
      .locator("xpath='text=edit'")
      .click();

    await expect(page).toHaveURL(/.*#edit/);
  });

  test("使用分步骤的 xpath 查找父元素", async ({ page }) => {
    const cell = page.locator("text=Adipisci5");
    const row = cell.locator("..");
    const editLink = row.locator("text=edit");

    await editLink.click();

    await expect(page).toHaveURL(/.*#edit/);
  });
});
```

如你所见,Playwright 在定位和处理父元素时提供了极大的灵活性。如果我遗漏了什么,请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上联系我并告诉我。

---

感谢阅读!如果你觉得这篇文章有帮助,请在 [LinkedIn](https://www.linkedin.com/mynetwork/discovery-see-all/?usecase=PEOPLE_FOLLOWS&followMember=butchmayhew) 上联系我,或考虑[给我买杯咖啡](https://ko-fi.com/butchmayhew)。如果你想收到更多内容直接发送到你的收件箱,请在下方订阅。

## 来源

URL 来源: https://playwrightsolutions.com/how-do-you-locate-the-parent-of-an-element-with-playwright/

发布时间: 2023-02-13
