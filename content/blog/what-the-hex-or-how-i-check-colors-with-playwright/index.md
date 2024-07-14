+++
date = 2023-10-30
title = "Hex是什么鬼, 我该怎么用playwright去检查控件的颜色"
description = "省流: toHaveCss()断言"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

![图片2](https://playwrightsolutions.com/content/images/2023/10/2023-10-29_11-28-26-1.jpg)

别担心，这不是一个你必须在红色和蓝色之间选择的《黑客帝国》场景。我是一个视觉型的人，用图表、图片或者更好的面部表情来解释事情对我来说更容易。由于互联网还没有准备好展示我的面部表情，让我们用图片来说明。

在运行我的登录检查时，Playwright 做得非常好。它使用我们的数据测试 ID 找到“登录”按钮并点击它。然而，我正在开发的应用程序允许终端用户自定义颜色，这意味着管理员可以更改按钮和背景的颜色。这不是我每次发布都想测试的事情，所以我必须测试一下 Playwright 的能力。我能否用 Playwright 轻松检查按钮的颜色？还是最终不得不使用 JavaScript 去搞定？

事实证明，您可以检查按钮的颜色。只需使用 `.toHaveCSS()` [(官方文档链接)](https://playwright.dev/docs/api/class-locatorassertions#locator-assertions-to-have-css)

当然，我不会只给你上面的链接然后祝你好运。让我们一起为按钮写一个断言。

一切都从检查你想要检查颜色的元素开始。在我们的例子中，这是“登录”按钮，这是它在开发者工具中的样子：

![图片3](https://playwrightsolutions.com/content/images/2023/10/2023-10-29_12-01-45.jpg)

当您点击元素时，会发现很多 CSS 属性。这里有一个有用的技巧：使用右侧样式标签中的搜索框并输入“background”或“color”以过滤出您需要的特定属性。

如您所见，在此示例中，背景色不仅是蓝色，而是“#031df4”。这是该特定颜色的**十六进制**代码。  
_❤️ 如果你现在有点迷茫，你可以简单地搜索“十六进制颜色代码解释”，然后回来更好地理解。_

根据文档，我们有我们需要的一切：

- locator（登录按钮）
- CSS 属性名称（`background-color`）
- CSS 属性值（`#031df4`）。

让我们编写检查并运行它：

![图片4](https://playwrightsolutions.com/content/images/2023/10/2023-10-29_13-29-33.jpg)

将十六进制颜色代码传递给 `.toHaveCSS()`

它失败了，因为 `.toHaveCSS()` 期望你传递特定格式的 RGB 颜色作为`background-color`。  
_❤️ 如果你现在有点迷茫，你可以简单地搜索“RGB 颜色代码解释”，并且也许“RGB vs hex”以更好地理解。_

你需要将十六进制颜色代码转换为 RGB 颜色代码。快速搜索搜索后，我找到了一个不需要使用库的简单解决方案：

```typescript
export function convertHexToRGB(hex) {
  // 如果输入中包含 '#'，则将其删除
  hex = hex.replace(/^#/, "");

  // 将十六进制值解析为单独的 R、G 和 B 值
  const red = parseInt(hex.substring(0, 2), 16);
  const green = parseInt(hex.substring(2, 4), 16);
  const blue = parseInt(hex.substring(4, 6), 16);

  // 以对象形式返回 RGB 值
  return {
    red: red,
    green: green,
    blue: blue,
  };
}
```

将十六进制转换为 RGB

我将其保存到我的 `./lib` 文件夹中，然后导入到规范文件中：

![图片5](https://playwrightsolutions.com/content/images/2023/10/2023-10-29_13-25-50.jpg)

将十六进制转换为 RGB -> console.log(RGB 颜色) -> 在 `.toHaveCSS()` 检查中使用 RGB 颜色

测试通过了！现在，我有一个检查，以确保按钮的颜色正是我期望的。我还添加了对禁用按钮的检查。这样，如果禁用按钮的代码发生变化，我将是第一个知道的人。（注意：在我的应用程序中，禁用按钮没有使用`background-color`属性，而是使用`color`属性，因此始终要勤勉并首先手动检查属性。）

如果您在一个规范文件中有多个 `.toHaveCSS()` 断言，最好将它们抽象到您的“./lib”文件夹（或您保留固定装置的任何地方）中，以提高代码的可读性。

```
export async function checkColor(element, cssProperty, rgbColors) {
  await expect(element).toHaveCSS(cssProperty, `rgb(${rgbColors.red}, ${rgbColors.green}, ${rgbColors.blue})`);
}
```

将断言移到 ./lib 文件夹中

最后，这是一个颜色检查如何在使用页面对象模式、抽象的 `convertHexToRGB()` 和 `checkColor()` 的规范文件中显示的示例：

![图片6](https://playwrightsolutions.com/content/images/2023/10/2023-10-29_13-37-29.jpg)

---

![图片7](https://playwrightsolutions.com/content/images/2023/10/checkingcolor.png)

## 来源

**来源链接**: [What the Hex, or How I Check Colors With Playwright](https://playwrightsolutions.com/what-the-hex-or-how-i-check-colors-with-playwright/)

**发布时间**: 2023-10-30
