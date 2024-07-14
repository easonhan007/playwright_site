+++
date = 2024-02-28
title = "Playwright 视觉测试终极指南"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

随着 Web 应用的不断完善,确保每次更新不会破坏前端展示变得愈发具有挑战性。面对众多浏览器、设备以及每个组件的无数状态,单元测试可以保证代码的一致性,ui 自动化测试可以确保系统的一致性,但它们都无法捕捉到视觉异常、布局问题或平台兼容性问题。

这就是视觉测试发挥作用的地方。视觉测试会存储被测应用 ui 的截图,并将其与应用的当前状态进行比较。不再有意外的 bug,不再需要在三种不同的浏览器和 12 种不同的 viewport 上进行开发。视觉测试自动化了这个过程,确保你的应用始终看起来完全正确。

本文将帮助你从视觉测试新手成长为专家。即使是专家也能在后面的章节中找到一些好处,因为我们将深入探讨测试、本地开发和 CI/CD 流程的独特策略。

本文的实现基于[Playwright](https://playwright.dev/),这是一个出色的开源 ui 自动化测试工具,支持所有浏览器和多种编程语言。它非常适合进行视觉测试。如果你还没有用过 Playwright,你应该尝试一下。

## 视觉测试常见问题

让我们先探讨一些关于视觉测试的常见问题。如果你只想要代码,可以直接跳到[视觉测试入门](https://www.browsercat.com/post/ultimate-guide-visual-testing-playwright#getting-started-with-visual-testing)。

### 什么是视觉测试?

视觉测试是一种通过比较应用当前截图与基准图像截图来自动验证应用视觉完整性的做法。它确保代码的更改不会在用户界面中引入意外结果。它还可以用于确保在不同浏览器和设备之间的一致性,以及确保你的应用保持可访问性和美观性。

视觉测试有时也被称为视觉回归测试、自动化视觉测试和截图测试。

### 视觉测试有什么好处?

视觉测试可以确保你的应用在快速开发期间保证站点的质量稳定。视觉测试可以捕捉到其他测试方法完全遗漏的 bug。而且由于这个过程是自动化的,视觉测试在回溯和修复 bug 方面可以节省大量的时间和精力。

### 视觉测试的最佳实践是什么?

视觉测试是一个简单的过程。你只需要在各种状态下存储应用和组件的截图,然后在代码更改后将这些截图与应用进行比较。只要你定期运行测试并使用良好的策略来更新截图,视觉测试就会非常管用。

### 视觉测试和单元测试有什么区别?

单元测试专注于特定代码接口的输入和输出,而视觉测试则关注用户界面本身。单元测试非常适合验证核心行为和边缘情况,但只有视觉测试才能确保用户可以使用这些功能并看到结果。

### 视觉测试和自动化测试有什么区别?

自动化测试确保应用的视图和组件按预期运行,而视觉测试确保这些视图和组件按预期显示。

端到端测试(自动化测试)使用 DOM 选择器定位元素,而人类使用眼睛。因此,虽然端到端测试可以确认按钮是否可点击,但只有视觉测试才能确认按钮是否可见并且在正确的位置上。

### 什么时候应该使用视觉测试?

随着应用的发展,视觉测试变得越来越有价值。在开发初期,你的 UI 处于不断变化中,所以视觉测试并不能提供很大的价值。但一旦你的应用开始稳定下来,视觉测试就成为了改变游戏规则的工具。

我建议逐步为那些几个月没有改变但今天需要修改的视图或组件添加视觉测试。在开始编码之前,为那些不应该因为你当前的工作而改变的组件添加视觉测试。然后你就可以自信地编码了!

### 视觉测试值得做吗?

是的,值得。随着 web 应用的发展,视觉测试是提升效能的重要尝试。例如,你可以开发一个测试套件,简单地比较同一个视图在不同浏览器和屏幕尺寸下的表现。有了这些测试,你就可以自信地对应用进行更改,而不需要同时打开三个浏览器。

### 视觉测试最好的工具是什么?

[Playwright](https://playwright.dev/)被广泛认为是浏览器自动化和集成测试的最佳测试框架。视觉测试也不例外。凭借强大的配置选项、对所有浏览器和多种编程语言的支持、直观的 API 以及庞大的社区,playwright 就是第一选择。

## 视觉测试入门

让我们从设置你的代码库开始,然后我们将编写一些测试。

这一部分应该不到 10 分钟就能开始。在继续阅读之前,我强烈建议你先完成 playwright 的安装工作,因为在指南的后面部分,你将能够亲自实践一些高级技巧。

### 1. 安装依赖

如果你已经安装了 Playwright,可以跳过这一步。

否则,安装你的依赖并创建一个示例测试文件:

```bash
# Install node dependencies
npm install -D @playwright/test
npm install -D typescript

# Install playwright browsers
npx playwright install

# Create the test file
mkdir -p tests
touch tests/homepage.spec.ts
```

### 2. 编写你的第一个视觉测试用例

打开`tests/homepage.spec.ts`并添加以下代码:

```javascript
import { test, expect } from "@playwright/test";

test("home page visual test", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  await expect(page).toHaveScreenshot();
});
```

### 3. 运行你的视觉测试

使用以下命令运行你的测试:

```bash
npx playwright test
```

第一次运行测试时,它们会失败并显示类似这样的错误消息:

```bash
Error: A snapshot doesn't exist at {TEST_OUTPUT_PATH}, writing actual.
```

这是符合预期的。因为 Playwright 之前没有保存过结果。`expect(page).toHaveSnapshot()`这段没东西可以比较,所以它必须使测试失败。但不用担心,下次运行测试时,Playwright 会将页面的当前状态与之前存储的截图进行比较。

所以再次运行你的测试:

```bash
npx playwright test
```

成功了!你应该看到类似这样的消息:

```bash
Running 1 test using 1 worker
  1 passed (6.6s)
```

如果你的测试失败了,花几分钟时间看看能否解决问题。如果不能,请继续阅读。我在本文后面介绍了许多故障排除技巧。

#### 截图存储在哪里?

默认情况下,测试截图与创建它们的测试文件存储在一起。

当视觉测试失败时,Playwright 会将"之前"图像、"之后"图像和"差异"图像存储在`./test-results`目录中。这些在后面调试失败的测试时会很有用。

(继续阅读以获取有关设置这些截图位置的建议。你可能不希望测试的截图散布在你的代码库中。)

### 4. 更新测试截图

太棒了!你的测试现在可以确认页面没有任何变化,但如果你真的想做一些更改怎么办?

要更新你的截图,请使用`--update-snapshots`(或`-u`)标志运行你的测试:

```bash
npx playwright test -u
```

这个命令将运行你的测试用例并更新截图并保存当前的截图作为基准图像。如果你现在运行这个命令,所有用例应该正常通过。

警告:这个命令会更新所有截图。你要非常小心,因为这很容易意外更新你不打算更新的截图。

#### 我如何只更新部分截图?

要更新一部分测试的截图,我们可以从 CLI 过滤测试。只有匹配的测试用例会被更新。

```bash
# Update tests with matching file name
npx playwright test -u "**/home*.spec.ts"

# Update tests with matching test name
npx playwright test -u --grep "home" --grep-invert "zzz"

# Updates tests within project
npx playwright test -u --project "chromium"
```

我们稍后会深入探讨截图管理,但现在,让我们专注于调试...

### 5. 调试视觉测试

我们知道如何更新失败测试的截图,但如果测试因为 bug 而失败时，我们该怎么办?

为了探索这种情况,让我们更新我们的测试用例,使截图比较断言失败:

```bash
test('home page visual test', async ({page}) => {
  await page.goto('https://www.browsercat.com');
  await expect(page).toHaveScreenshot({
    // crop the screenshot to a specific area
    clip: {x: 0, y: 0, width: 500, height: 500},
  });
});
```

现在让我们运行测试,要求 playwright 生成 HTML 报告:

```bash
npx playwright test --reporter html
```

运行该命令后,你的浏览器会自动打开测试报告。它应该显示失败的具体结果。

滚动到页面底部,你会看到这个小东西:

视觉测试差异

"差异"视图提供了预期和实际截图之间的鲜明对比。然而,我发现"滑块"视图对于实际修复问题最有用。

#### 我如何解释"差异"视图?

"差异"视图显示了预期和实际截图之间的差异。

黄色像素表示截图之间的变化,但它们在允许的差异阈值内。

红色像素超出了允许的差异阈值。默认情况下,即使只有一个红色像素也会导致测试失败。

有关配置这些阈值的建议,请跳转到[使视觉测试阈值更宽松这篇文章](https://www.browsercat.com/post/ultimate-guide-visual-testing-playwright#make-visual-tests-more-forgiving)。

#### 我必须使用 HTML 报告吗?

这不是必须的(尽管我建议使用)。无论你是否生成 HTML 报告,失败的视觉测试都会自动将"之前"、"之后"和"差异"图像输出到`./test-results`目录。

我经常在工作时直接在 VSCode 中打开"之前"图像。这样我就可以让浏览器专注于我的测试用例。

### 6. 使用 UI 模式进行快速视觉测试

Playwright 有一个行业领先的"UI 模式",它使处理测试变得非常简单。

虽然它有许多杀手级功能,但我最喜欢的是它在每一个步骤之后自动去截图的能力。这允许你快速调试你的测试。它还使得在正确的地方插入视觉断言变得非常容易。

要在 UI 模式下运行你的测试,使用以下命令:

```bash
npx playwright test --ui
```

我鼓励你探索 UI 模式,因为它很有用，而且功能丰富。

![图1: Playwright UI模式](https://res.cloudinary.com/browsercat/image/upload/c_fill,w_768/dpr_auto/f_auto/q_auto/v1/articles/pw-snapshot-ui-mode.png?_a=DATAdtTEZAA0)

好了!现在你已经对使用视觉测试有了初步了解,现在让我们带你从白带升级道黑带。在这个过程中,我们将使用一些 Playwright 的高级功能,编写出稳定的测试用例,微调我们的配置文件等等。

## 页面截图 vs 元素截图

Playwright 的视觉测试 API 允许你对整个页面或特定元素进行截图。

但什么时候应该使用前者，什么时候该使用后者呢?

### 什么时候应该使用页面截图?

页面截图非常适合验证整个页面是否按预期工作。使用页面截图来测试布局、响应是否正确和可访问性。

但要注意:页面截图的用例可能不是那么稳定。毕竟,如果 viewport 内的任何内容发生变化,整个截图都会失败。我们稍后会介绍最小化这些影响的策略,但现在,明智的做法是将页面截图视为一种强大但粗糙的工具。

你已经看到了页面截图的实际应用。这里是一个例子:

```javascript
test("page snapshot", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  await expect(page).toHaveScreenshot();
});
```

### 什么时候应该使用元素截图?

元素截图,正如你所期望的,专注于单个页面元素。这使它们非常适合测试单独的组件，或者验证元素在特定上下文中行为是否符合预期。元素截图比页面截图更不容易出现问题,但它们需要更多的前期工作来配置。毕竟,它们覆盖的范围比较有限，这也意味着你需要更多的截图才能覆盖与页面截图相同的范围。

以下是一个元素截图的例子:

```javascript
test("element snapshot", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  const $button = page.locator("button").first();
  await expect($button).toHaveScreenshot();
});
```

## 使用页面截图

让我们探索一些页面截图的有用功能和常见用例...

### 裁剪页面截图

有时候，验证测试结果不需要用到整个屏幕。因为屏幕的部分设计常常会变化，这可能导致原本稳定的测试变得不可靠。

在这些情况下,最好将你的截图裁剪到具体的区域。这里有一个例子:

```javascript
test("cropped snapshot", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  const { width, height } = page.viewportSize();

  await expect(page).toHaveScreenshot({
    // square at the center of the page
    clip: {
      x: (width - 400) / 2,
      y: (height - 400) / 2,
      width: 400,
      height: 400,
    },
  });

  await expect(page).toHaveScreenshot({
    // top slice, maximum possible width
    clip: { x: 0, y: 0, width: Infinity, height: 16 },
  });
});
```

### 对整个页面进行截图，而不是当前屏幕截图

默认情况下,Playwright 会对当前屏幕进行截图。

我们也可以对整个页面截图（自动滚动到页面的最下方），具体使用场景是: 例如,如果你要测试一个页面在不同浏览器中看起来是否相同,最简单的解决方案就是对整个页面进行截图。而且对于这种测试,你不会存储之前运行的截图,所以你的用例相对稳定。

以下是如何进行完整页面截图:

```javascript
test("full page snapshot", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  await expect(page).toHaveScreenshot({
    fullPage: true,
  });
});
```

### 在进行页面截图之前滚动

在使用页面截图时,你经常会想在视觉断言之前把页面滚动到某个具体的元素。

以下是方法:

```javascript
test("scroll before snapshot", async ({ page }) => {
  await page.goto("https://www.browsercat.com");

  await page.evaluate(() => {
    document
      .querySelector("#your-element")
      ?.scrollIntoView({ behavior: "instant" });
  });

  await expect(page).toHaveScreenshot();
});
```

注意:虽然 Playwright 有一个`.scrollIntoViewIfNeeded()`方法,但它不会将元素滚动到 viewport 的顶部。所以我推荐上面的解决方案。它将充分利用你的 viewport 并确保你的截图在不同运行之间保持一致。

## 使用元素截图

元素截图比页面截图更"深入细节"。它们带来了很多力量和灵活性。

让我们探索一些例子...

### 测试元素交互性

随着你的组件库的增长,越来越难跟踪库中每个元素的每种状态。

在下面的例子中,我们对表单输入在各种状态下进行截图:

```
test('element states', async ({page}) => {
  await page.goto('https://www.browsercat.com/contact');
  const $textarea = page.locator('textarea').first();

  await expect($textarea).toHaveScreenshot();
  await $textarea.hover();
  await expect($textarea).toHaveScreenshot();
  await $textarea.focus();
  await expect($textarea).toHaveScreenshot();
  await $textarea.fill('Hey, cool cat!');
  await expect($textarea).toHaveScreenshot();
});
```

### 测试元素响应性

在处理响应式设计时,确保你的元素在全范围的屏幕尺寸下看起来都很好是很重要的。

使用元素截图来确保你的组件在各种断点下看起来都很好。

```
test('element responsiveness', async ({page}) => {
  const viewportWidths = [960, 760, 480];
  await page.goto('https://www.browsercat.com/blog');
  const $post = page.locator('main article').first();

  for (const width of viewportWidths) {
    await page.setViewportSize({width, height: 800});
    await expect($post).toHaveScreenshot(`post-${width}.png`);
  }
});
```

## 高级截图技巧

页面和元素截图共享许多常见的配置选项。让我们探讨其中最有用的...

### 屏蔽截图的部分内容

有时,你会想要排除截图的某些部分。一个子元素或子区域可能经常变化,包含敏感信息,或者与测试无关。例如,时间戳、动画、用户电子邮件地址或轮换广告。

Playwright 提供了"屏蔽"这些区域的能力,用一种不太可能与你网站内容混淆的鲜艳颜色替换它们。

这里有一个例子:

```
test('masked snapshots', async ({page}) => {
  await page.goto('https://www.browsercat.com');
  const $hero = page.locator('main > header');
  const $footer = page.locator('body > footer');

  await expect(page).toHaveScreenshot({
    mask: [
      $hero.locator('img[src$=".svg"]'),
      $hero.locator('a[target="_blank"]'),
    ],
  });

  await expect($footer).toHaveScreenshot({
    mask: [
      $footer.locator('svg'),
    ],
  });
});
```

这是第一个屏蔽截图的样子:

![图2: 屏蔽截图](https://res.cloudinary.com/browsercat/image/upload/c_fill,w_768/dpr_auto/f_auto/q_auto/v1/articles/pw-snapshot-masked.png?_a=DATAdtTEZAA0)

### 在截图期间保持样式不变

视觉测试之所以有价值，是因为它们可以捕捉到应用外观的意外变化。但有些页面元素本身就不稳定，无法直接包含在测试中。

幸运的是,我们可以在截图期间加载一些基本的 CSS,以限制或隐藏页面中的有问题元素或者难搞定的元素。

这里是方法:

```javascript
test("consistent styles", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  const $hero = page.locator("main > header");

  await expect(page).toHaveScreenshot({
    stylePath: [
      "./hide-dynamic-elements.css",
      "./disable-scroll-animations.css",
    ],
  });

  await expect($hero).toHaveScreenshot({
    stylePath: [
      "./hide-dynamic-elements.css",
      "./disable-scroll-animations.css",
    ],
  });
});
```

### 自动重试不稳定的用例

在处理动画或动态内容时，视觉测试可能会变得不稳定。特别是大型页面截图容易受到影响。

Playwright 可以在一定时间内自动重试失败的视觉测试，直到找到有效的匹配。启用该功能的方法如下：

```javascript
test("retry snapshots", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  const $hero = page.locator("main > header");

  await expect(page).toHaveScreenshot({
    // retry snapshot until timeout is reached
    timeout: 1000 * 60,
  });

  await expect($hero).toHaveScreenshot({
    // retry snapshot until timeout is reached
    timeout: 1000 * 60,
  });
});
```

### 下载图片进行比较断言

在 99.9%的情况下，页面和元素截图可以满足你的需求。但有时你可能需要断言任意图像在不同测试运行之间保持一致。

例如，你的应用可能生成二维码或社交分享卡片，或者你可能需要压缩和转换用户上传的头像。在这些情况下，你会希望确保这些功能运行正常，不会出问题。

对此使用`expect().toMatchSnapshot()`:

```javascript
import { test, expect } from "@playwright/test";
import { buffer } from "stream/consumers";

test("arbitrary snapshot", async ({ page }) => {
  // generates custom avatars — fun!
  await page.goto("https://getavataaars.com");
  await page.locator("main form button").first().click();

  // download the avatar
  const avatar = await page
    .waitForEvent("download")
    .then((dl) => dl.createReadStream())
    .then((stream) => buffer(stream));

  expect(avatar).toMatchSnapshot("avatar.png");
});
```

### 比较不同浏览器之间的截图

到目前为止，我们编写的所有测试都是比较代码更改前后应用的状态。但如果你想比较应用在不同浏览器和设备之间的状态呢？

为了实现这一点，我们将利用 Playwright 的“项目”功能。项目允许你定义具有独特配置的自定义测试套件。在成熟的代码库中，你可能会有很多这样的项目用于不同的设备、环境和测试策略。

让我们来点魔法！

首先，更新你的 playwright.config.ts。如果你还没有，请在项目根目录创建它：

```javascript
const crossBrowserConfig = {
  testDir: "./tests/cross-browser",
  snapshotPathTemplate: ".test/cross/{testFilePath}/{arg}{ext}",
  expect: {
    toHaveScreenshot: { maxDiffPixelRatio: 0.1 },
  },
};

export default defineConfig({
  // other config here...

  projects: [
    {
      name: "cross-chromium",
      use: { ...devices["Desktop Chrome"] },
      ...crossBrowserConfig,
    },
    {
      name: "cross-firefox",
      use: { ...devices["Desktop Firefox"] },
      dependencies: ["cross-chromium"],
      ...crossBrowserConfig,
    },
    {
      name: "cross-browser",
      use: { ...devices["Desktop Safari"] },
      dependencies: ["cross-firefox"],
      ...crossBrowserConfig,
    },
  ],
});
```

在配置 snapshotPathTemplate 以确保所有浏览器的截图存储在相同的位置后，每个测试都将其截图与相同的源图像进行比较。

接下来，在 ./tests/cross-browser/homepage.spec.ts 创建一个新的测试文件：

```javascript
import { test, expect } from "@playwright/test";

test("cross-browser snapshots", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  await page.locator(":has(> a figure)").evaluate(($el) => $el.remove());

  await expect(page).toHaveScreenshot(`home-page.png`, {
    fullPage: true,
  });
});
```

为了避免失败,让我们初始化我们的新截图:

```bash
npx playwright test --project cross-browser -u
```

然后让我们运行测试:

```bash
npx playwright test --project cross-browser
```

你的所有测试都通过了吗？可能并没有，因为在不同环境下，不同的浏览器会以不同方式渲染字体、颜色和图像，即使你的应用表现正常。

如果你的测试失败了，你可能需要调整截图的 `maxDiffPixelRatio` 和 `threshold` 选项。想要调试这个问题，请查看[如何使视觉测试更宽松](https://www.browsercat.com/post/ultimate-guide-visual-testing-playwright#make-visual-tests-more-forgiving)。

## 视觉测试的各种选项

因为视觉测试非常敏感,所以掌握它们的配置很重要。让我们探讨一些最有用的选项...

### 自定义截图文件名

Playwright 根据测试的名称自动命名你的截图。如果你只将截图用于视觉测试,那就没问题。

然而,许多用户喜欢将这些图像重新用于文档和测试报告。这些任务久需要自定义文件名。

这样命名你的截图:

```javascript
test("custom snapshot names", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  const $hero = page.locator("main > header");

  await expect(page).toHaveScreenshot("home-page.png");
  await expect($hero).toHaveScreenshot("home-hero.png");

  const $footer = page.locator("body > footer");
  const footImg = await $footer.screenshot();

  expect(footImg).toMatchSnapshot("home-foot.png");
});
```

注意:自定义截图名称并不能完全控制文件名,除非你还配置了自定义目录。使用默认配置,Playwright 会在你的文件名后添加一个后缀,以确保它们在不同项目中是唯一的。

### 自定义截图目录

默认情况下,Playwright 将截图存储在创建它们的测试文件所在的目录中。这种方法有许多缺点:

- 你的代码库会变得很乱。
- 很难从版本控制中排除截图文件。
- 不容易在 CI/CD 运行之间缓存结果。
- 对自定义截图文件名不友好。

所以让我们告诉 Playwright 将我们的截图存储在一个自定义目录中。更新你的`playwright.config.ts`文件:

```javascript
export default defineConfig({
  snapshotPathTemplate: ".test/snaps/{projectName}/{testFilePath}/{arg}{ext}",
});
```

使用上面的配置,如果我们的测试文件路径是`./tests/homepage.spec.ts`,Playwright 会将我们的截图存储如下:

```bash
.test/
  snaps/
    tests/
      homepage.spec.ts/
        home-page.png
        home-hero.png
        home-foot.png
```

使用这种模式,你可以从版本控制中排除你的截图,可以在 CI/CD 中缓存你的结果,并且可以在它们出现时轻松查看失败的测试。

阅读 Playwright 文档中关于[截图路径模板](https://playwright.dev/docs/api/class-testconfig#test-config-snapshot-path-template)中提供的更多选项。

### 使视觉测试更宽松

默认情况下,视觉测试非常严格。如果有一个像素失败,你的测试就会失败。幸运的是,Playwright 提供了多个选项来调整你的视觉测试的敏感度。

具体选项有:

- `threshold`: 单个像素必须变化多少才被认为是不同的。值是从`0`到`1`的百分比,默认为`0.2`。
- `maxDiffPixels`: 在测试仍然通过的情况下可以不同的最大像素数。默认情况下,此选项是禁用的。
- `maxDiffPixelRatio`: 在测试仍然通过的情况下可以不同的最大像素百分比。值是从`0`到`1`的百分比,但默认情况下此选项是禁用的。

你可以全局或基于每个断言去调整这些选项。

#### 全局配置阈值

还是在`playwright.config.ts`文件:

```javascript
export default defineConfig({
  expect: {
    toHaveScreenshot: {
      threshold: 0.25,
      maxDiffPixelRatio: 0.025,
      maxDiffPixels: 25,
    },
    toMatchSnapshot: {
      threshold: 0.25,
      maxDiffPixelRatio: 0.025,
      maxDiffPixels: 25,
    },
  },
});
```

#### 重写每个断言的阈值

这样做可以重写全局截图设置的值:

```javascript
test("forgiving snapshots", async ({ page }) => {
  await page.goto("https://www.browsercat.com");
  const $hero = page.locator("main > header");

  await expect(page).toHaveScreenshot({
    maxDiffPixelRatio: 0.15,
  });

  await expect($hero).toHaveScreenshot({
    maxDiffPixels: 100,
  });
});
```

#### 我如何调整这些选项?

要找到适合你应用的最佳设置，请仔细查看测试生成的"差异"图像。在这些图像中，黄色像素表示在可接受范围内的差异，而红色像素则表示导致测试失败的差异。

首先，尝试提高`threshold`值，看是否能消除截图中的红色像素。但要谨慎：过高的`threshold`可能会导致错误地忽略重要差异。建议不要将其设置超过`0.35`，这已经是相当高的值了。

如果调整`threshold`没有效果，就重点关注`maxDiffPixelRatio`和`maxDiffPixels`这两个参数。在使用这些选项时，要权衡利弊。

`maxDiffPixelRatio`是相对于图像大小的比例，因此更可能在各种不同大小的图像中都能产生良好的结果。这使它成为全局设置的理想选择——但前提是要谨慎设置！毕竟，允许整个页面图像 10%的差异可能会导致过大的变化被忽视。

相比之下，`maxDiffPixels`是一个固定的像素值，可以让你更精确地控制单个测试。但如果将其应用于全局设置，即使数值很小也可能带来风险。对于小图像来说，较高的`maxDiffPixels`可能会占据图像的很大比例。

在调整这些参数时，要根据你的具体需求和图像特征，找到最佳平衡点。

## CI/CD 中的视觉测试

太棒了!你已经在本地成功运行了视觉测试,并对结果很有信心。现在是时候将这些测试整合到你的 CI/CD 流程中了。

你可能会觉得这听起来不太容易。毕竟,你需要一种方法在不同的测试运行期间保存截图,还需要让你的 CI/CD 流程知道何时应该更新截图缓存。

不过别担心,我已经为你准备好了解决方案。:)

在这个例子中,我们假设你使用的是 GitHub Actions。不过即使你使用其他 CI/CD 服务提供商,操作步骤也大同小异。

那么,让我们开始吧!

### 1. 为 CI/CD 配置 Playwright

你的 CI/CD 环境与本地开发环境存在差异,我们需要在 Playwright 配置中对此作出相应调整。

请使用以下设置 来更新你的 `playwright.config.ts` 文件。你可以将这些新选项与你之前设置的其他选项自由组合:

```javascript
import { defineConfig, devices } from "@playwright/test";

const isCI = !!process.env.CI;

export default defineConfig({
  timeout: 1000 * 60,
  workers: isCI ? 1 : "50%",
  retries: isCI ? 2 : 0,
  forbidOnly: isCI,

  outputDir: ".test/spec/output",
  snapshotPathTemplate:
    ".test/spec/snaps/{projectName}/{testFilePath}/{arg}{ext}",
  testMatch: "*.spec.{ts,tsx}",

  reporter: [
    [
      "html",
      {
        outputFolder: ".test/spec/results",
        open: "never",
      },
    ],
    isCI ? ["github"] : ["line"],
  ],
});
```

这些配置选项主要考虑了以下几个方面:

1. CI 环境资源限制:
   CI 环境通常资源有限,这会导致测试运行速度变慢,稳定性降低。因此,我们需要调整相关参数来适应这种情况。

2. 测试输出整理:
   我们将所有测试输出都组织到`.test`目录中,这样可以方便进行缓存管理。记得将`.test/`添加到你的`.gitignore`文件中,因为这些内容不应该提交到代码仓库。

3. 报告生成:
   在 CI/CD 环境中,我们会生成两种类型的报告:
   - `html`报告: 这种报告对于深入调试非常有用。
   - `github`报告: 这种报告提供简洁的输出,便于快速查看结果。

### 2. 在 CI/CD 中运行你的测试

接下来,让我们创建一个基本的流水线。它还不能做所有事情,但它是一个很好的快速开始模版。

在`.github/workflows/visual-tests.yml`创建一个文件:

```yaml
name: Visual Tests

on:
  push:
    branches:
      - "*"

  pull_request:
    branches:
      - "*"

jobs:
  run-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          cache: pnpm
          node-version-file: .nvmrc
          check-latest: true

      - name: Install deps
        run: |
          npm install
          npx playwright install

      - name: Test
        run: npx playwright test --ignore-snapshots
```

注意我们使用`--ignore-snapshots`标志运行测试。由于我们没有办法在测试运行之间存储截图,这实际上是让我们的测试通过的唯一方法。

如果你现在将你的代码推送到 Github,工作流将直接运行,并且它会通过,但它不会做任何的测试验证。

让我们来解决这个问题...

### 3. 在运行之间存储截图

为了确保我们的视觉测试能够正常运行，我们需要在不同的测试运行之间保存截图。为此，我们将利用 GitHub 的"artifacts"功能来缓存这些截图。

其次，我们还要编写一个步骤，用于在截图不存在时生成新的截图。这样可以解决我们的测试在新分支上首次运行时可能出现的失败问题。

最后，我们将重新启用截图断言，让视觉测试发挥其应有的作用。

以下是具体的更新内容：

```yaml
- name: Install deps
  run: |
    npm install
    npx playwright install

- name: Set up cache
  id: cache
  uses: actions/cache@v4
  with:
    key: cache/${{github.repository}}/${{github.ref}}
    restore-keys: cache/${{github.repository}}/refs/heads/master
    path: .test/**

- name: Initialize snapshots
  if: ${{steps.cache.outputs.cache-hit != 'true'}}
  run: npx playwright test --update-snapshots

- name: Test
  run: npx playwright test
```

请注意，我们的缓存键不仅包含当前分支的信息，还包括了对`master`分支的回退机制。这样设计的好处是，当新分支首次推送时，它也能有一些基本的东西可以使用。

如果你现在触发 CI/CD 流程，你会观察到以下情况：

1. 在第一次运行时：

   - 系统会生成新的截图
   - 测试会通过
   - 缓存会被更新

2. 在后续的运行中：
   - 系统会命中缓存
   - 不会生成新的截图
   - 测试仍然会通过

到目前为止，一切看起来都很顺利。但是，我们还需要考虑一个重要问题：当截图需要更新时，我们该如何处理呢？

### 4. 触发截图更新

现在我们有了真正有效的视觉测试,让我们更新我们的工作流,以便我们可以按需更新截图。

首先,让我们参数化我们的工作流...

```yaml
on:
  push:
    branches:
      - "*"

  pull_request:
    branches:
      - "*"

  # Allow updating snapshots during manual runs
  workflow_call:
    inputs:
      update-snapshots:
        description: "Update snapshots?"
        type: boolean

  # Allow updating snapshots during automatic runs
  workflow_dispatch:
    inputs:
      update-snapshots:
        description: "Update snapshots?"
        type: boolean
```

`workflow_call`允许我们手动触发工作流,选择是否更新截图。`workflow_dispatch`允许其他 Github 工作流使用相同的配置。

以下是手动小组件的样子:

![图3: 手动Github工作流](https://res.cloudinary.com/browsercat/image/upload/c_fill,w_768/dpr_auto/f_auto/q_auto/v1/articles/pw-snapshot-github-trigger.png?_a=DATAdtTEZAA0)

让我们对"Initialize snapshots"（初始化截图）步骤进行更新，使其能够在特定参数启用时触发截图更新。具体更新如下：

```yaml
- name: Initialize snapshots
  if: ${{steps.cache.outputs.cache-hit != 'true' || inputs.update-snapshots == 'true'}}
  run: npx playwright test --update-snapshots --reporter html
```

最后，让我们把生成的 HTML 报告作为 artifact 上传。这样做有两个重要的好处：

- 在决定是否需要更新工作流中的截图之前，我们可以先参考这份报告。
- 如果遇到问题需要调试，这份报告也会成为很有价值的参考资料。

```yaml
- name: Test
  continue-on-error: true
  run: npx playwright test

- name: Upload test report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: playwright-report
    path: .test/spec/results/
    retention-days: 30
    overwrite: true
```

注意我们的"Test"步骤现在启用了`continue-on-error`,这样即使测试失败,我们也可以上传我们的报告。

我们新增了一个"Upload test report"（上传测试报告）步骤，它的作用是将报告作为 artifact 上传。这样做之后，你会发现在工作流的结果页面中出现了一个新的链接。这个链接会直接指向一个 zip 文件，里面包含了我们刚刚生成的测试报告。

![图4: Github工作流报告](https://res.cloudinary.com/browsercat/image/upload/c_fill,w_768/dpr_auto/f_auto/q_auto/v1/articles/pw-snapshot-github-artifact.png?_a=DATAdtTEZAA0)

### 5. 大幅提升你的 CI/CD 流水线速度！

目前一切进展顺利，但我们还能做一件事让视觉测试更上一层楼：_让它们飞速运行_！

你可能已经注意到两个步骤正在拖慢你的流水线：

1. 安装 Playwright 浏览器。
2. 串行运行测试。

幸运的是，我们可以不用花钱而很容易的解决这两个问题。

[BrowserCat](https://www.browsercat.com/hosted-playwright) 在云端托管了一批 Playwright 浏览器，你只需几行代码就能连接使用。

如果你这样做，就不必在 CI/CD 环境中安装浏览器，而且可以完全并行运行测试。

最棒的是？BrowserCat 提供了一个*超赞的*永久免费计划。除非你有一个庞大的团队，否则你可能永远不用花一分钱。

那么让我们开始吧！

首先，在 [BrowserCat](https://app.browsercat.com/) 注册一个免费账户。

其次，创建一个 [API 密钥](https://app.browsercat.com/keys)，并将其作为名为 `BROWSERCAT_API_KEY` 的秘密存储在你的 Github 仓库中。你可以通过导航到你的仓库，点击"Settings"，然后"Secrets"，再点"Actions"，最后点"New repository secret"来完成这一步。

第三，让我们更新 `playwright.config.ts` 以使用 BrowserCat：

```javascript
const isCI = !!process.env.CI;
const useBC = !!process.env.BROWSERCAT_API_KEY;
export default defineConfig({
  timeout: 1000 * 60,
  workers: useBC ? 10 : isCI ? 1 : '50%',
  retries: useBC || isCI ? 2 : 0,
  maxFailures: useBC && !isCI ? 0 : 3,
  forbidOnly: isCI,
  use: {
    connectOptions: useBC ? {
      wsEndpoint: 'wss://api.browsercat.com/connect',
      headers: {'Api-Key': process.env.BROWSERCAT_API_KEY},
    },
  },
});
```

在上面的更新中，你会注意到我们在使用 BrowserCat 时将并行化增加到了 10 个工作进程。这是一个不错的起点，但你可以毫无问题地大幅增加这个数值。

注意，只要定义了 `BROWSERCAT_API_KEY`，这个配置就会连接到 BrowserCat。这对于在本地和 CI/CD 中运行测试都很有用。

好了，现在是最后一点魔法...让我们停止每次运行流水线时安装 Playwright 的浏览器：

```yaml
- name: Install deps
  run: npm install
```

如果你现在运行你的流水线，即使你的测试套件中只有一个测试，你也会看到显著的速度提升。而且每月 1000 个免费积分，你可以连续运行流水线数小时，还有大量时间剩余。

## 接下来的步骤...

呼！你已经走了很长的路。

到这一步，你能做的唯一一件提高视觉测试技能的事就是练习。赶紧去截图吧！

这里有一些很棒的链接可以帮助你：

- [Playwright 视觉比对](https://playwright.dev/docs/test-snapshots)
- [expect(page).toHaveScreenshot()](https://playwright.dev/docs/api/class-pageassertions#page-assertions-to-have-screenshot-1)
- [expect(locator).toHaveScreenshot()](https://playwright.dev/docs/api/class-locatorassertions#locator-assertions-to-have-screenshot-1)
- [expect(image).toMatchSnapshot()](https://playwright.dev/docs/api/class-snapshotassertions#snapshot-assertions-to-match-snapshot-1)
- [TestConfig.expect](https://playwright.dev/docs/api/class-testconfig#test-config-expect)
- [BrowserCat 博客](https://www.browsercat.com/blog)

祝你自动化测试愉快！

## 来源

URL 来源: https://www.browsercat.com/post/ultimate-guide-visual-testing-playwright

发布时间: 2024-02-28
