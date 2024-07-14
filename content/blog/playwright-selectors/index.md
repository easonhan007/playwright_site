+++
date = 2024-01-24
title = "Playwright 选择器终极指南"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

## 写在前面

**👀 乙醇来自 2024 年的评论。这篇文章不是特别推荐，里面讲了很多 xpath 和 css 选择器的高级应用，不过 xpath 是 playwright 不推荐使用的方式，css 在 playwright 里的地位也不高，playwright 最推荐的定位器其实是[这几个](https://playwright.dev/docs/locators#quick-guide)**

在 Playwright 中,选择器是用于定位和交互网页元素的字符串标识符。它们对于执行表单填写、网页爬取和自动化测试等任务至关重要。

Playwright 是一个开源的自动化库,专为端到端测试、网页爬取和 ui 自动化测试而设计。它支持无头和有头浏览器模式,并通过快速易用的 API 提供出色的性能。

Playwright 兼容多种浏览器,包括 Chrome、Microsoft Edge (使用 Chromium)、Safari (使用 WebKit) 和 Mozilla Firefox。Playwright 提供不同类型的选择器,包括 CSS 选择器、XPath 选择器和文本选择器,每种选择器都有其优势和适用场景。

![图片 1: playwright-meme](https://bugbug-homepage.s3.eu-central-1.amazonaws.com/playwright_meme_api_17fe7e4658.jpeg)

## **概要**

- 本指南涵盖了不同类型的选择器,包括 CSS、XPath 和文本选择器,并解释了它们的用法和优势。
- 还提供了创建可靠和可维护的自动化脚本的最佳实践。

**另请查看:**

[15 大无代码自动化测试工具](https://bugbug.io/blog/software-testing/codeless-automation-testing-tools/)

[Testim 替代品](https://bugbug.io/blog/test-automation-tools/testim-alternatives/)

[Cypress 替代品](https://bugbug.io/blog/test-automation-tools/cypress-alternative/)

## Playwright 入门

要开始使用 Playwright,你需要安装它并设置一个项目。

**以下是步骤指南:**

1.  为你的 Playwright 项目创建一个新文件夹。
2.  在终端或命令行界面中打开该文件夹。
3.  运行命令 `npm init -y` 来初始化一个新的 Node.js 项目。
4.  通过运行命令 `npm install playwright` 来安装 Playwright。
5.  导入 Playwright 并创建一个新的浏览器实例。

```javascript
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  // your code here
  await browser.close();
})();
```

安装好 Playwright 后,你就可以开始使用选择器与网页元素进行交互了。如果你想了解更多关于使用 Playwright 的信息,可以查看我们的 [Playwright 速查表](https://bugbug.io/blog/software-testing/playwright-cheat-sheet/)。

## Playwright 中的定位器 API

Playwright 的定位器 API 是自动等待和重试功能的核心,使得与网页元素的交互更加稳定。以下是关于它的一些要点:

1.  **创建定位器**: 定位器使用 `page.locator()` 方法创建。此方法接受一个描述如何在页面中查找元素的选择器。Playwright 支持 CSS 和 XPath 选择器,如果省略 `css=` 或 `xpath=` 前缀,它会自动检测。
2.  **可操作性检查**: 在执行操作之前,Playwright 会对元素进行可操作性检查。这包括确保元素是可见的、attached 的和稳定的。例如,在点击一个元素时,Playwright 会等待它变为可点击状态。
3.  **具体的操作行为**: 在执行诸如 `click` 或 `dblclick` 等操作时,你可以指定各种选项:

- `position`: 相对于元素左上角的 x 和 y 坐标。
- `timeout`: 等待操作完成的最长时间(以毫秒为单位)。默认为 30 秒,但你可以传入 0 来禁用超时。
- `trial`: 当设置为 true 时,该方法会执行可操作性检查而不执行实际的操作。这对于确保元素已准备好进行交互很有用。

4.  **点击和双击**: `click` 方法用于点击元素,你可以指定鼠标按钮、点击次数、鼠标按下和释放之间的延迟,以及修饰键(如 Shift、Control)等选项。`dblclick` 方法类似,但执行双击操作。
5.  **元素数量**: `count` 方法返回匹配给定选择器的元素数量,有助于断言检查页面上特定元素的数量。
6.  **通过 text、Alt text titile 以及 testID 定位**: 你以根据元素的文本内容、alt 文本、title 属性或 textID 来定位元素。这对于查找非交互元素(如 `div`、`span`、`p` 等)以及具有特定标题或 textID 的图像和元素特别有用。
7.  **Shadow DOM**: Playwright 中的定位器默认可以与 Shadow DOM 中的元素一起工作,但 XPath 选择器 不支持这个特性。
8.  **filter**: 你可以通过文本、子元素是否存在或其他条件来过滤定位器。当你需要从列表或一组元素中选择特定项目时,这很有用。

Playwright 中的定位器 API 旨在尽可能模仿用户交互,使其成为编写可靠和可维护测试用例的强大工具。如需更详细的信息,你可以参考 Playwright 官方文档中关于[定位器](https://playwright.dev/docs/locators)和定位器方法的部分。

## Playwright CSS 选择器

**CSS 选择器**是 Web 开发中的一个主要工具,在 Playwright 中广泛用于定位网页中的元素。这些选择器是代表不同元素的字符串,基于元素的属性、class 或 ID。

**Playwright CSS 选择器**与常规 CSS 中的选择器类似,但为 Web 自动化进行了增强,允许精确定位元素。它们能够匹配包含指定属性或类的任何元素,其语法与传统 CSS 非常相似。这包括复杂的选择器,如伪类,它们是 Playwright 中的实验性 CSS 功能。

此外,Playwright 支持属性选择器操作符,并可以解析将多个空格转换为一个空格的行为,确保空格始终被标准化。

1.  **基本 CSS 选择器用法**:

- Playwright 可以使用标准 CSS 语法定位元素。

  `await page.locator('css=button').click();`

2.  **穿透 Shadow DOM**:

- Playwright 中的 CSS 选择器可以穿透开放的 Shadow DOM,允许访问 shadow dom 元素。

3.  **自定义伪类**:

- Playwright 引入了 `:visible`、`:has-text()`、`:has()`、`:is()`、`:nth-match()` 等伪类。
- `:visible` 只针对可见元素。

`await page.locator('button:visible').click();`

- `:has-text()` 匹配包含指定文本的元素,对于不区分大小写、去除空格的子字符串匹配很有用。

  `await page.locator('article:has-text("Playwright")').click();`

4.  **通过文本匹配**:

- `:text()` 伪类匹配包含指定文本的元素。

  `await page.locator('#nav-bar :text("Home")').click();`

- `:text-is()` 匹配具有完全相同文本的元素。

  `await page.locator('#nav-bar :text-is("Home")').click();`

- `:text-matches()` 匹配文本内容符合类似 JavaScript 正则表达式的元素。

  `await page.locator('#nav-bar :text-matches("reg?ex", "i")').click();`

5.  **包含其他元素的元素**:

- `:has()` 伪类是 Playwright 中的实验性 CSS 功能。如果元素包含由选择器指定的其他元素,它会返回该元素。

  `await page.locator('article:has(div.promo)').textContent();`

6.  **基于布局匹配元素**:

- Playwright 的布局伪类如 `:right-of()`、`:left-of()`、`:above()`、`:below()` 和 `:near()` 可用于根据元素与其他元素的空间关系选择元素。

`await page.locator('input:right-of(:text("Password"))').fill('value');`

7.  **从查询结果中选择第 N 个匹配项**:

- `:nth-match()` 伪类从多个匹配项中选择特定实例的元素。

`await page.locator(':nth-match(:text("Buy"), 3)').click();`

这些功能使 Playwright 中的 CSS 选择器成为 Web 自动化的强大工具,不仅允许基于元素的属性和文本内容精确定位元素,还可以根据它们的可见性、包含关系和相对位置进行定位。

这种多样性在复杂的 Web 应用程序中特别有用,因为标准选择器功能有限，扩展之后才更好用一点。

## Playwright 中的 XPath 选择器

**XPath 选择器**为 Playwright 中的元素定位提供了另一种强大的方法。与 CSS 选择器不同,XPath 选择器基于网页的 dom 结构。它们允许你根据元素的位置、属性和其他条件来查找元素,xpath 可以精确地遍历 DOM。这在 CSS 选择器可能不够用的情况下特别有用,比如复杂布局或需要查找包含指定文本的元素的时候。

**Playwright 中的 XPath** 还支持自定义选择器引擎,为选择很难通过 CSS 去定位的元素提供了灵活性。

你可以使用 BugBug 的**无代码** [**在线 XPath 生成器**](https://bugbug.io/xpath-selector-builder/)来创建稳定的 xpath 选择器。

- **通过 XPath 选择元素**:

你可以使用元素的 XPath 来选择元素,这允许基于 DOM 结构进行更灵活和精确的定位。

`const elementByXPath = await page.$x('//div[@class="example"]');`

- **评估 XPath 表达式**:

Playwright 可以解析 XPath 表达式并返回匹配的元素。$x 是 Playwright 为此目的提供的一种简写方法。

`const elements = await page.$x('//button[contains(text(), "Submit")]');`

- **在 XPath 中使用 Axes**:

XPath 的 Axes 方法可以用于以各种方式遍历 DOM,例如选择相对于当前节点的父元素、兄弟元素或子元素。

`const siblingElement = await page.$x('//input[@id="username]/following-sibling::input');`

- **带条件表达式的 XPath**:

XPath 选择器可以包含条件来匹配具有特定属性或文本内容的元素。

`const elementWithCondition = await page.$x('//div[@data-status="active" and text()="Active"]');`

- **选择 Shadow DOM 内的元素**:

虽然 XPath 本身不支持 Shadow DOM,但 Playwright 允许使用 CSS 和 XPath 选择器的组合来实现定位 shadow dom 中的元素。

另外请查看我们的比较: [XPath vs CSS 选择器](https://bugbug.io/blog/test-automation/xpath-vs-css-selectors/)

## Playwright 中的 text 选择器

Playwright 中的**text 选择器**专注于根据可见文本内容定位元素。这些选择器非常适合定位包含特定文本节点的元素,或搜索具有精确内容的文本节点。

Playwright 中文本选择器的**语法**非常直观,允许你直接指定要匹配的文本,可以用单引号或双引号转义。这个功能在网页自动化脚本中特别有用,因为通过文本内容识别元素比使用属性或 XPath 更实用。

## 在 Playwright 中组合选择器

Playwright 还支持多个选择器的组合,这个功能增强了元素选择的精确度。通过将选择器链接在一起,你可以创建更具体的查询。这可能涉及组合 CSS 和 XPath 选择器,或使用同一类型的多个选择器并增加过滤条件来精确定位元素。

例如,你可以根据元素的布局和相对于其他元素的位置来选择元素,或者结合属性选择器和文本选择器来查找包含指定文本的元素。链式选择器解析满足链中所有条件的元素,组合的方式可以非常的灵活。

**定位器 API** 在 Playwright 中简化了与网页元素交互的过程,提供了一种更稳定和强大的方式来查询和操作页面元素。这在动态页面应用中,以及需要复杂交互的场景中特别有用。

## Playwright 中的高级选择器

除了 CSS 选择器和 XPath 选择器,Playwright 还支持一系列高级选择器,提供更大的灵活性。这些高级选择器包括 React 选择器、可访问性选择器、CSS 伪类和 XPath 函数。

**以下是 Playwright 中一些高级选择器的概述:**

- **React 选择器**: 用于识别 React 应用程序中的元素。
- **可访问性选择器**: 用于根据元素的可访问性属性定位元素。
- **CSS 伪类**: 用于根据各种状态或条件选择元素。
- **XPath 函数**: 用于使用 XPath 函数执行复杂查询。

Playwright 的高级选择器允许你微调元素选择并处理更复杂的场景。

## 在 Playwright 中使用选择器的最佳实践

为了充分利用 Playwright 选择器,遵循最佳实践很重要。以下是一些需要记住的提示:

- **使用唯一标识符**: 尽可能依赖唯一标识符(如 ID 或数据属性)来定位元素。
- **避免不稳定的选择器**: 应避免使用容易变化的选择器,比如基于位置关系的选择器。
- **定期更新选择器**: 定期检查并更新你的选择器,以适应网站结构的任何变化。

通过遵循这些最佳实践,你可以确保自动化脚本的稳定性和可靠性。

## 在 Playwright 中使用选择器进行自动化

Playwright 选择器对于表单填写、网页爬虫和 ui 自动化测试等任务非常有价值。让我们探讨几个在 Playwright 中使用选择器进行自动化的例子:

### 表单填写

这个脚本演示了浏览器自动化的基本套路,特别是启动浏览器、跳转到页面和与网页元素交互。需要注意的是,这个脚本并没有导航到特定的 URL,所以如果你打算将它用于特定网站,你需要添加一行使用 `page.goto('被测网站 URL')` 来访问该网站。

```javascript
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const usernameInput = await page.locator('#username');
  await usernameInput.fill('johndoe');

  const passwordInput = await page.locator('#password');
  await passwordInput.fill('password123');

  await browser.close();\
})();
```

### 网页爬虫

下面的代码展示了如何使用 Playwright 的自动化功能提取和打印网页上所有链接 'a' 元素的文本内容。

脚本首先从 Playwright 导入 Chromium 模块,然后启动一个 Chromium 浏览器实例并打开一个新页面。它使用 `$$eval` 函数选择页面上的所有超链接元素,并将它们的文本内容映射到一个数组。然后遍历这个数组,将每个链接的文本内容打印到控制台。

最后,脚本关闭浏览器页面。

```javascript
const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const links = await page.$$eval("a", (links) =>
    links.map((link) => link.textContent)
  );

  for (const linkText of links) {
    console.log(linkText);
  }

  await page.close();
})();
```

### ui 自动化测试

下面的代码是一个使用 Chromium 浏览器进行网页登录的 Playwright 脚本。

脚本首先导入 Playwright 模块并启动 Chromium 浏览器。然后它打开一个新的浏览器页面。

接下来,脚本通过各自的 ID `#username` 和 `#password` 定位页面上的用户名和密码输入字段,并用预定义的数据 'johndoe' 和 'password123' 填充它们。

填写登录信息后,脚本定位并点击登录按钮 `#loginButton`。然后它等待退出登录按钮 `#logoutButton` 出现,把这个当成是成功登录的断言。

最后,脚本关闭浏览器页面。这个自动化脚本是 Playwright 如何用于自动化网页应用登录程序的基本示例。

```javascript
const { chromium } = require('playwright');

(async () => {\
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const usernameInput = await page.locator('#username');
  await usernameInput.fill('johndoe');

  const passwordInput = await page.locator('#password');
  await passwordInput.fill('password123');

  const loginButton = await page.locator('#loginButton');
  await loginButton.click();

  const logoutButton = await page.locator('#logoutButton');
  await expect(logoutButton).toBeVisible();

  await page.close();\
})();
```

## 在 Playwright 中使用选择器处理 Shadow DOM

Playwright 的 CSS 和文本引擎可以穿透 Shadow DOM,允许你与元素交互,就像 shadow dom 不存在一样。这种能力简化了在 Shadow DOM 内选择和操作元素的过程。

对于定位 Shadow DOM 中的元素,可以直接使用 Playwright 的标准定位器,如 `page.locator()`、`page.getByText()` 等。例如,如果你有一个带有 shadow root 的自定义 Web 组件,想要点击其中的特定元素,你可以使用 `page.getByText('Details').click()` 来定位文本为 'Details' 的元素。同样,要点击像 `<x-details>` 这样的自定义元素,你可以使用 `page.locator('x-details', { hasText: 'Details' }).click()`。

Playwright 还支持高级选择器策略,比如通过文本、子/后代元素过滤定位器,或使用布局伪类如 `:right-of()`、`:left-of()`、`:above()`、`:below()` 和 `:near()` 来根据元素相对于其他元素的布局定位元素。当元素缺乏明显的属性或文本内容时,这些伪类特别有用,允许你指定它们的相对位置以进行更精确的选择。

此外,Playwright 为 React 和 Vue 应用程序提供了专门的定位器,分别以 `_react` 和 `_vue` 前缀识别。这些定位器允许你根据组件名称和属性值查找元素,这在测试这些框架的现代 Web 应用程序时特别方便。

重要的是要注意,虽然 XPath 可以在 Playwright 中使用,但它不能穿 shadow root,并且通常不鼓励使用,我们还是要使用更稳定、对用户可见的定位器。

## 结论

Playwright 选择器是进行自动化网页测试、网页抓取和用户界面测试任务的强大工具。通过利用 CSS 选择器、XPath 选择器和文本选择器,你可以精确定位网页上的元素并与之交互。

通过遵循最佳实践并利用 Playwright 选择器的高级功能,你可以简化自动化脚本并提高其可靠性。今天就开始使用 Playwright 选择器,释放你的自动化工作的全部潜力。

记住要定期更新你的选择器,使用唯一标识符,并探索 Playwright 选择器引擎中的各种选项,以使你的自动化脚本更加高效和稳健。

**祝你(自动化)测试愉快!**

## 常见问题解答: Playwright 选择器和定位器

### Playwright 支持哪些选择器?

Playwright 支持多种选择器来选择元素,以满足不同的 Web 自动化需求。这些包括:

- CSS 选择器: 根据 CSS 属性定位元素。Playwright 的 CSS 选择器工作方式类似于常规 CSS,但针对自动化进行了增强。
- XPath 选择器: 适用于复杂的 DOM 结构,XPath 选择器可以根据元素的 XML 路径导航和查找元素。
- 文本选择器: 定位包含指定文本的元素,非常适合查找文本节点或具有精确文本内容的元素。
- Playwright 特定选择器: 这包括像 data-test-id 这样的选择器,用于以 Playwright 框架特定的方式定位元素。
- React 选择器: 为 React 应用程序设计的选择器,允许与 React 组件交互。
- 属性选择器: 这些选择器使用属性选择器操作符,可以根据属性匹配任何元素。
- 链式选择器: 组合多个选择器,如 CSS 和 XPath,以解决更复杂的选择场景。
- 布局选择器: 依赖元素的布局和相对位置,使用诸如边界客户矩形等进行计算。

### 如何在 Playwright 中选择元素?

在 Playwright 中选择元素通常涉及使用代表上述选择器之一的字符串。例如:

- CSS 选择器: `page.$('.className')` 根据类选择元素。
- XPath 选择器: `page.$x('//div')` 使用 XPath 语法查找元素。
- 文本选择器: `page.$('text=Example')` 查找包含指定文本的元素。
- 组合选择器: 链接选择器如 `page.$('div.className > span')` 以定位特定元素内的元素。

### 什么是 Playwright 定位器或选择器?

Playwright 定位器或选择器是用于在 Web 自动化脚本中选择元素的基于字符串的工具。选择器是 Playwright 识别要交互的元素的方式,无论是点击、读取内容还是输入数据。它们可以很简单,比如文本选择器,也可以很复杂,比如链接 CSS 和 XPath 的链式选择器。

### 我们可以在 Playwright 中使用 XPath 吗?

是的,XPath 在 Playwright 框架中得到完全支持。它可以用于执行精确的元素选择,特别是在 CSS 选择器可能不够用的场景中。Playwright 中的 XPath 选择器可以使用各种 Axes、谓词和函数来导航 DOM,定位根据结构和内容(包括文本节点和属性)定位元素非常有用。例如,`page.$x('//button[@id="submit"]')` 将定位 ID 为 "submit" 的按钮。

## 来源

URL 来源: https://bugbug.io/blog/testing-frameworks/playwright-selectors/
