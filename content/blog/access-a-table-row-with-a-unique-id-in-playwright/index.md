+++
date = 2022-03-13
title = "如何在playwright中定位表格的行(table row)"
description = "可以用css来定位css=tr:has-text()"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

有许多不同的方法可以与表格进行交互，这是我们在 Playwright 测试中提取/确认数据是否存在的众多示例中的第一个。在这个示例中，我们将使用 https://letcode.in/table 上的表格。

![](https://playwrightsolutions.com/content/images/2022/03/image.png)

在这个挑战中，我想获取包含 Cupcake 值的整行。Playwright 有一个非常好的定位器函数，它允许我们指定一个高级元素 tr 并找到包含文本 Cupcake 的表格行。这将返回表格行的定位器，以便进行断言或以其他方式与整行进行交互。

TODO: 下面的代码应该已经失效了

```typescript
import { test } from "@playwright/test";

test("从单元格中的文本获取表格的整行", async ({ page }) => {
  await page.goto("https://letcode.in/table");

  const row = page.locator('tr:has-text("Cupcake")');
});
```

如果你 `console.log(row.innerText())`，你会得到如下返回值。

```
Cupcake
305
4
67
4
50
```

## 来源

[网址来源](https://playwrightsolutions.com/access-a-table-row-with-a-unique-id-in-playwright/)

发布时间: 2022-03-13
