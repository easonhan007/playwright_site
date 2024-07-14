+++
date = 2022-07-06
title = "如何在 Playwright 测试中根据条件不同使用 afterEach"
description = " 如何在 Playwright 测试中有条件地使用 afterEach"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在某些情况下，你可能希望在测试中使用 afterEach 来清理数据，但并非所有情况下都需要清理数据。我的具体例子是我在测试一个 POST 接口时，我们有正面和负面的测试。当我成功创建一个 POST 时，我希望在 afterEach 中删除刚刚创建的内容，但当我进行负面测试时，POST 并没有创建新的项目，我不需要运行 afterEach 来清理数据，因为它会因为试图删除不存在的 id 而失败。

解决方案是使 afterEach 有条件的被调用。请看下面的代码示例，我们创建了一个新变量`triggerAfterEach`，并设置为`true`来触发 afterEach。如果在测试中没有分配`triggerAfterEach`，afterEach 代码将不会执行。

```javascript
test.describe("测试组", async () => {
  let triggerAfterEach: boolean;

  test.afterEach(async () => {
    if (triggerAfterEach) {
      //在这里执行after代码
    }
  });

  test("有afterEach的测试场景", async () => {
    triggerAfterEach = true;
  });

  test("没有afterEach的测试场景", async () => {
    triggerAfterEach = false;
  });
});
```

## 来源

[URL Source](https://playwrightsolutions.com/how-to-conditionally-use-aftereach/)

Published Time: 2022-07-06
