+++
date = 2023-11-06
title = "如何使用 Faker 快速创建真实数据"
description = "如何在playwright中使用facker库"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在测试注册流程或填写表单时,输入一个简单的"Jane Doe"很容易。但当你还需要输入电子邮件、地址,并在不同的语言环境中完成这些操作时,事情就变得复杂了。

当然,你可以自己创建测试数据集,但为什么不直接用代码生成呢?

这正是 [Faker](https://fakerjs.dev/) 的用途:它可以生成从姓名、地址到公司名称的任何信息。它能为你的测试创造处逼真的假数据。

Faker 是一个 Node.js 库,所以让我们用 `npm install --save-dev @faker-js/faker` 来安装它

```javascript
import { faker } from "@faker-js/faker/locale/en";

const randomName = faker.person.fullName(); // Rowan Nikolaus
const randomEmail = faker.internet.email(); // Kassandra.Haley@erich.biz
```

生成假数据的函数一般是按领域分组的:个人、公司、地点、日期等。

## 与 Playwright 的集成

在 Playwright 测试中使用 Faker 非常简单:

```javascript
import { faker } from "@faker-js/faker/locale/en";
import { expect, test } from "@playwright/test";

test.describe("测试应用程序", () => {
  test("应该使用用户名和密码创建账户", async ({ page }) => {
    const username = faker.internet.userName();
    const password = faker.internet.password();
    const email = faker.internet.exampleEmail();

    // 访问网页并创建账户
    await page.goto("https://www.example.com/register");
    await page.getByLabel("email").fill(email);
    await page.getByLabel("username").fill(username);
    await page.getByLabel("password", { exact: true }).fill(password);
    await page.getByLabel("confirm password").fill(password);
    await page.getByRole("button", { name: "Register" }).click();

    // 现在,我们尝试使用这些凭据登录
    await page.goto("https://www.example.com/login");
    await page.getByLabel("email").fill(email);
    await page.getByLabel("password").fill(password);
    await page.getByRole("button", { name: "Register" }).click();

    // 我们应该成功登录到仪表板页面
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
```

## seed 设置

每次测试运行时,你都会获得新的数据。但有时,你可能希望数据不那么随机。例如,如果你进行截图对比测试,每次值都发生变化会导致测试失败。

[![图片 1: xkcd 图像:一个返回 4 的 getRandomNumber 函数。评论说"通过公平骰子选择。保证随机"](https://imgs.xkcd.com/comics/random_number.png)](https://xkcd.com/221/)

梗图：不那么随机 👆

为了保持测试的确定性,你需要[为 Faker 的随机生成器设置 seed](https://fakerjs.dev/api/faker.html#seed),并在每次测试之间重置它。

这里有一个文件,包含一个设置了 seed 的测试(总是相同的值)和一个随机测试:

```javascript
import { faker } from "@faker-js/faker/locale/en";
import { expect, test } from "@playwright/test";

// 这将在每次测试后重新为我们的 faker 实例设置种子
test.afterEach(() => {
  faker.seed();
});

test("使用设置种子的 Faker 生成熊", () => {
  // 用一个静态数字为我们的 faker 实例设置种子
  faker.seed(123);
  const animal = faker.animal.bear();

  console.log(animal);
  expect(animal).toMatchSnapshot();
});

test("随机生成熊", () => {
  const animal = faker.animal.bear();

  console.log(animal);
});
```

让我们检查结果,这里有 3 次运行:每个浏览器一次。

```bash
> npx playwright test
使用 1 个工作进程运行 6 个测试

  ✓  1 [chromium] › seed.spec.ts:9:1 › 使用设置种子的 Faker 生成熊 (75ms)
亚洲黑熊
  ✓  2 [chromium] › seed.spec.ts:18:1 › 随机生成熊 (65ms)
大熊猫
  ✓  3 [firefox] › seed.spec.ts:9:1 › 使用设置种子的 Faker 生成熊 (62ms)
亚洲黑熊
  ✓  4 [firefox] › seed.spec.ts:18:1 › 随机生成熊 (29ms)
美洲黑熊
  ✓  5 [webkit] › seed.spec.ts:9:1 › 使用设置种子的 Faker 生成熊 (58ms)
亚洲黑熊
  ✓  6 [webkit] › seed.spec.ts:18:1 › 随机生成熊 (27ms)
眼镜熊

  6 个测试通过 (2.5s)
```

如你所见,`使用设置种子的 Faker 生成熊`这个用例是截图对比的测试用例。它顺利通过,并且在之后的每次运行中都会通过。控制台输出始终是`亚洲黑熊`。

`随机生成熊`的控制台输出在每次测试运行时的结果都不一样。这是因为每次测试后,我们都重置了 Faker 的种子。

你可以在 Faker 的文档中的[可重现结果](https://fakerjs.dev/guide/usage.html#reproducible-results)部分查看更多详情。

## 总结

Faker 是一个方便的库,用于生成假的但是看起来又很真实的数据。我们已经了解了它的基本用法,以及如何将其添加到我们的测试中,而且还知道了可以通过设置 seed 来控制随机性。事实证明,Faker 与 Playwright Test 一起使用非常简单!

---

嗨!我是 Jean-François,我是一名前端技术主管。我帮助团队在提高敏捷性和技术卓越性。我对软件工程和测试感兴趣。
你可以在 [https://jfgreffier.com](https://jfgreffier.com/) 找到我

## 来源

URL 来源: https://playwrightsolutions.com/how-to-quickly-get-realistic-data-with-faker-for-playwright-tests/

发布时间: 2023-11-06T13:30:29.000Z
