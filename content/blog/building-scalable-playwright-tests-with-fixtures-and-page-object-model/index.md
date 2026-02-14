+++
date = 2026-02-14
title = "Playwright 测试进阶：用 Fixtures 优雅实现 Page Object Model"
description = "让测试代码更简洁、可复用、可扩展"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "Page Object", "Fixture"]
[extra]
math = false
image = "2026-02-14-20-03-24.png"
+++

在 Playwright 项目中，传统 Page Object Model 很容易导致代码重复和维护困难。

本文手把手教你如何利用 Playwright 的自定义 Fixtures，把 Page 对象自动注入测试，彻底消除每次使用page前都要手动去 `new` 的烦恼。

让测试代码更简洁、可复用、可扩展。

跟着做完，你的自动化测试框架将提升一个档次！特别适合用在大型的项目里面。

预计耗时：20–40 分钟

### 1. 理解两种常见写法及其问题

**传统 POM 写法**（大家最开始都会这么写）

```ts
// pages/LoginPage.ts
export class LoginPage {
  constructor(private page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto("https://example.com/login");
  }

  async login(username: string, password: string) {
    await this.page.fill("#username", username);
    await this.page.fill("#password", password);
    await this.page.click("#login");
  }
}
```

```ts
// tests/login.spec.ts
import { test, expect } from "@playwright/test";
import { LoginPage } from "../pages/LoginPage";

test("应该能正常登录", async ({ page }) => {
  const loginPage = new LoginPage(page); // 每份测试都要 new 一次

  await loginPage.goto();
  await loginPage.login("testuser", "password");

  await expect(page).toHaveURL("https://example.com/home");
});
```

**痛点**（项目大了之后特别明显）：

- 每份测试都要写 `new XXXPage(page)`
- 改一次构造函数 → 所有测试文件都要改
- 想做「已登录状态」的前置条件 → 每个测试重复写登录代码
- 测试文件看起来很“重”

### 2. Playwright 推荐的现代写法：把 Page Object 做成 Fixture

核心思路：  
**不要在测试里手动 new Page Object，而是让 fixture 帮你创建并注入**

#### 步骤 1 – 保持 Page Object 类不变（或稍作调整）

```ts
// pages/LoginPage.ts
export class LoginPage {
  constructor(public page) {} // 保持 public 方便 fixture 里访问 page.url() 等

  locators = {
    username: "#username",
    password: "#password",
    loginBtn: "#login",
  };

  async goto() {
    await this.page.goto("https://example.com/login");
  }

  async fillCredentials(username: string, password: string) {
    await this.page.fill(this.locators.username, username);
    await this.page.fill(this.locators.password, password);
  }

  async submit() {
    await this.page.click(this.locators.loginBtn);
  }

  // 常用组合动作（可选）
  async login(username: string, password: string) {
    await this.goto();
    await this.fillCredentials(username, password);
    await this.submit();
  }
}
```

#### 步骤 2 – 创建自定义 fixture（最核心的一步）

新建文件：`fixtures/index.ts`（或 `utils/fixtures.ts`）

```ts
// fixtures/index.ts
import { test as base } from "@playwright/test";
import { LoginPage } from "../pages/LoginPage";

// 可以继续扩展其他 page 对象
type MyFixtures = {
  loginPage: LoginPage;
  // inventoryPage: InventoryPage;
  // cartPage: CartPage;
};

export const test = base.extend<MyFixtures>({
  // 普通注入（页面刚打开的状态）
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await use(loginPage); // 交给测试使用，用完自动清理（如果有 teardown 逻辑）
  },

  // 进阶：自动完成登录的 fixture（非常实用）
  // authenticatedLoginPage: async ({ page }, use) => {
  //   const loginPage = new LoginPage(page);
  //   await loginPage.login('standard_user', 'secret_sauce');
  //   await use(loginPage);
  // },
});

export { expect } from "@playwright/test";
```

#### 步骤 3 – 在测试文件中使用超级干净的写法

```ts
// tests/login.spec.ts
import { test, expect } from "../../fixtures"; // 注意路径

test("普通登录流程验证", async ({ loginPage }) => {
  await loginPage.goto();
  await loginPage.fillCredentials("testuser", "password");
  await loginPage.submit();

  await expect(loginPage.page).toHaveURL(/home$/);
});

// 更推荐的写法：把组合动作放在 Page 类里
test("使用封装的 login 方法", async ({ loginPage }) => {
  await loginPage.login("testuser", "password");

  await expect(loginPage.page).toHaveURL("https://example.com/home");
});
```

### 3. 进阶用法推荐（强烈建议掌握）

#### 3.1 自动登录 fixture（最常用场景）

```ts
// fixtures/index.ts 继续扩展
export const test = base.extend<MyFixtures>({
  loginPage: async ({ page }, use) => { ... },

  loggedInPage: async ({ loginPage }, use) => {
    await loginPage.login('standard_user', 'secret_sauce');
    // 可选：等待页面稳定
    await loginPage.page.waitForURL(/inventory/);
    await use(loginPage.page);   // 这里注入 page，也可以注入 loginPage
  },
});
```

测试里直接用已登录状态：

```ts
test("已登录用户能看到商品列表", async ({ loggedInPage }) => {
  await expect(loggedInPage.locator(".inventory_list")).toBeVisible();
});
```

#### 3.2 多个 Page Objects 一起使用

```ts
type MyFixtures = {
  loginPage: LoginPage;
  inventoryPage: InventoryPage;
  cartPage: CartPage;
};

export const test = base.extend<MyFixtures>({
  loginPage: async ({ page }, use) => { ... },
  inventoryPage: async ({ page }, use) => {
    await use(new InventoryPage(page));
  },
  // 可以依赖其他 fixture
  cartPage: async ({ inventoryPage }, use) => {
    // 假设从 inventory 页加商品后进入 cart
    await inventoryPage.addFirstItemToCart();
    await inventoryPage.gotoCart();
    await use(new CartPage(inventoryPage.page));
  },
});
```

### 4. 总结：为什么推荐这种写法？

| 技能点       | 传统 new Page() 写法   | 使用 Fixture + POM 写法             |
| ------------ | ---------------------- | ----------------------------------- |
| 重复 new     | 每个测试都要写         | 只写一次（在 fixture 里）           |
| 构造函数修改 | 所有测试文件改         | 只改 fixture 文件                   |
| 前置登录     | 每个测试重复写登录代码 | 做成 loggedInPage fixture，一行搞定 |
| 可读性       | 中等                   | 很高（测试里只看到业务动作）        |
| 扩展性       | 差（文件越来越多越乱） | 很好（fixtures 集中管理）           |
| 执行速度     | 每次都重新创建对象     | Playwright 缓存复用（同 worker 内） |

### 5. 快速上手 checklist

- [ ] 创建 `pages/` 目录，放所有 Page 类
- [ ] 创建 `fixtures/index.ts`，用 `test.extend()` 定义 fixture
- [ ] 测试文件里 `import { test, expect } from '../fixtures'`
- [ ] 把常用前置操作（登录、导航）尽量做成 fixture
- [ ] Page 类里多放组合方法（login、addToCart、checkout 等）

祝你写出优雅、可维护的 Playwright 测试！🚀
