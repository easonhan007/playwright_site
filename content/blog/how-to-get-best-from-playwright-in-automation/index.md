+++
date = 2024-09-27
title = "playwright自动化的一些最佳实践"
description = "比较基础"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++
Playwright 是一个强大的网页自动化和测试工具，支持多种浏览器和平台。为了充分发挥 Playwright 的优势，你需要遵循一些最佳实践，以确保测试代码易于管理、可靠且具备可扩展性。以下是一些提升 Playwright 测试自动化的关键建议。

1. **使用页面对象模型（POM）**

页面对象模型（POM）是一种设计模式，通过将页面交互与测试逻辑分离来组织测试代码。采用 POM 可以集中管理与页面的交互逻辑，若界面发生变化，只需更新一次页面对象，而无需修改多个测试。

```javascript
class LoginPage {  
  constructor(private page: Page) {}
  
  async login(username: string, password: string) {  
    await this.page.fill('#username', username);  
    await this.page.fill('#password', password);  
    await this.page.click('#login-button');  
  }  
}
```

2. **避免硬编码值**

尽量避免在测试中硬编码敏感信息或网址。使用环境变量或配置文件可以使测试更加灵活，并便于在不同环境中运行。这种做法提高了测试的可移植性，并使其能够适应环境的变化。

```javascript
const config = {  
  use: {  
    baseURL: process.env.BASE_URL || '<your app URL>',  
  }  
};  
export default config;
```

3. **利用fixture**

Fixture允许你设置一些公共状态，例如已登录用户或浏览器配置，这些状态可以在多个测试中重用。这样可以减少代码重复，提高测试的整洁性和执行速度。

```javascript
import { test as base } from '@playwright/test';

const test = base.extend({  
  loggedInPage: async ({ page }, use) => {  
    await page.goto('/login');  
    await page.fill('#username', 'demo');  
    await page.fill('#password', 'test123');  
    await page.click('#login-button');  
    await use(page);  
  }  
});

test('带有登录用户的测试', async ({ loggedInPage }) => {
  // 在这里编写你的登录代码
});
```

4. **并行运行测试**

并行运行测试可以节省时间，尤其是当测试用例较多时。可以通过 `workers` 设置来配置同时运行的测试数量。

```javascript
const config = {  
  workers: 4,  // 将同时运行 4 个测试用例  
};  
export default config;
```

5. **处理不稳定测试的重试机制**

有时测试会因为网络问题或时间问题而失败。你可以配置测试在失败时自动重试，这样可以避免虚假失败并减少不稳定测试的数量。

```javascript
const config = {  
  retries: 2,  // 这将在失败时重试两次  
};  
export default config;
```

6. **使用内置断言**

Playwright 提供内置断言，帮助你验证条件，例如文本内容或元素的可见性。利用 Playwright 的断言可以提高测试性能，并提供更好的错误报告。

```javascript
await expect(page).toHaveURL('https://google.com');  
await expect(page.locator('#header')).toHaveText('Google!');
```

7. **跨浏览器测试**

Playwright 支持在不同浏览器（如 Chromium、Firefox 和 WebKit）中运行测试。确保配置测试套件在所有支持的浏览器中运行，以捕捉特定浏览器的问题。

```javascript
const config = {  
  projects: [  
    { name: 'chromium', use: { browserName: 'chromium' } },  
    { name: 'firefox', use: { browserName: 'firefox' } },  
    { name: 'webkit', use: { browserName: 'webkit' } },  
  ],  
};  
export default config;
```

8. **避免测试间的依赖**

测试应该是独立的，能够任意顺序执行。避免编写依赖于其他测试结果或状态的测试。独立的测试更容易维护，也更可靠。

9. **使用显式等待而非硬等待**

与其使用固定延迟（`page.waitForTimeout()`），不如使用显式等待，例如 `page.waitForSelector()` 或 Playwright 的内置断言。显式等待确保在满足条件时立即继续执行测试，从而提高速度和可靠性。

```javascript
await page.waitForSelector('#element', { state: 'visible' });
```

10. **利用浏览器上下文进行测试隔离**

浏览器上下文允许你在同一浏览器内的隔离环境中运行测试，这样可以确保测试之间不会相互干扰，例如共享 cookies 或会话，从而提高可靠性和效率。

```javascript
const context = await browser.newContext();  
const page = await context.newPage();
```

11. **优化定位器**

使用稳定且唯一的定位器与网页元素进行交互。避免使用容易失效的定位器，如类名或索引，应该选择更可靠的选项，例如文本或 `data-testid` 属性。稳定的定位器减少了用户界面变化时需要更新测试的频率。

```javascript
await page.click('button:has-text("Submit")');  
await page.click('[data-testid="login-button"]');
```

12. **合理配置超时**

根据应用程序的性能调整全局或单个测试的超时设置。这可以避免由于超时而导致的测试失败，并确保测试能够灵活应对较慢的环境，例如 CI 流水线。

```javascript
const config = {  
  timeout: 30000,  // 超时设置为 30 * 1000 秒  
};  
export default config;
```

遵循这些最佳实践可以帮助你构建一个强大且可扩展的 Playwright 测试自动化套件。通过编写清晰、可靠且易于维护的测试，你将提升测试的速度和质量，使应用程序更加稳定，并让开发过程更为高效。
