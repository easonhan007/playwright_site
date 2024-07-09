+++
date = 2024-07-09
title = "Playwright可以做API测试吗？当然可以✌️"
description = "如何使用playwright从零开始一个 API 自动化测试项目"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

大家好。很长时间没见了，今天我要和大家聊聊我最近一直在使用的一个框架：Playwright。几乎每个从事测试领域的人都听过 Playwright 的名字。但在大多数测试自动化项目中，Playwright 被用于 UI 测试。经过团队的一些研究，我们决定为什么不将其用于 API 测试自动化项目呢，并开始了研究。到目前为止，我们有一个不错的项目成功地运行了 API 测试。让我告诉你如何从零开始一个 API 测试自动化项目。我们可以通过几个示例来结束这个话题。

## 安装

在安装 Playwright 之前，请确保你的环境中安装了 **node.js**。

```bash
# 安装 playwright
npm install @playwright/test

# 创建一个空项目目录
mkdir api-test-project
cd api-test-project
npm init -y
```

让我们以一个预订接口为例。我假设我们将在这个结构中测试 GET、POST 和 DELETE 请求。在创建项目结构时，有一点需要注意。我们需要避免在构建结构时重复代码。我们应该尽量编写尽可能干净和可读的代码。因此，我选择将我的服务和测试分开存放。

**项目结构大致如下：**

```
booking-api-test/
 ├── tests/
 │ ├── get-booking.spec.ts
 │ ├── post-booking.spec.ts
 │ ├── delete-booking.spec.ts
 │ └── ...
 ├── services/
 │ ├── api-service.ts
 │ ├── auth-service.ts
 │ └── ...
 ├── package.json
 ├── tsconfig.json
 └── .env
```

> 现在让我们编写服务和测试代码。我将假设这个结构中有身份验证。对于这种身份验证，我假设 Headers 中有一个 accessToken 值。

## 步骤 2：创建服务文件

```typescript
//api-service.ts

import { Page } from "@playwright/test";
export class APIService {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async getBooking(bookingId: string) {
    return await this.page.route(`**/bookings/${bookingId}`).fetch();
  }

  async createBooking(accessToken: string, bookingData: any) {
    return await this.page.route("**/bookings").fetch({
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(bookingData),
    });
  }

  async deleteBooking(accessToken: string, bookingId: string) {
    return await this.page.route(`**/bookings/${bookingId}`).fetch({
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  }
}

// auth-service.ts

import { Page } from "@playwright/test";
export class AuthService {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async getAccessToken(username: string, password: string) {
    // 获取访问令牌所需的 API 调用
    // 例如，你可以使用 OAuth 2.0 进行身份验证
  }
}
```

## 步骤 3：创建 API 测试文件

现在我们可以创建测试文件。作为示例，让我们创建 **get-booking.spec.ts**、**post-booking.spec.ts** 和 **delete-booking.spec.ts** 文件。

```typescript
//get-booking.spec.ts

import { test, expect } from '@playwright/test';
import { APIService, AuthService } from '../services';

test('GET Booking Test', async ({ page }) => {
const authService = new AuthService(page);
const accessToken = await authService.getAccessToken('username', 'password');

const apiService = new APIService(page);
const response = await apiService.getBooking('bookingId', accessToken);

// 测试断言
expect(response.status()).toBe(200);
const bookingData = await response.json();
expect(bookingData).toHaveProperty('id', 'bookingId');
});

## post-booking.spec.ts

import { test, expect } from '@playwright/test';
import { APIService, AuthService } from '../services';

test('POST Booking Test', async ({ page }) => {
const authService = new AuthService(page);
const accessToken = await authService.getAccessToken('username', 'password');

const bookingData = {
// 预订数据
// 根据你的接口，你可以传递所需的数据
};

const apiService = new APIService(page);
const response = await apiService.createBooking(accessToken, bookingData);

// 测试断言
expect(response.status()).toBe(201);
const createdBooking = await response.json();
expect(createdBooking).toHaveProperty('id');
});

// delete-booking.spec.ts

import { test, expect } from '@playwright/test';
import { APIService, AuthService } from '../services';

test('DELETE Booking Test', async ({ page }) => {
const authService = new AuthService(page);
const accessToken = await authService.getAccessToken('username', 'password');

const apiService = new APIService(page);
const response = await apiService.deleteBooking('bookingId', accessToken);

// 测试断言
expect(response.status()).toBe(204);
});
```

这个结构实际上向你展示了如何非常简单地获取 accessToken，然后如何使用它。我试图以一种简单的方式解释它。也可以采取其他路径。

创建项目结构可能会根据你和你正在处理的项目有所不同。例如，你可以全局处理这个问题，而不必在每个测试中调用一个方法来访问 accessToken。

**注意：Playwright 像其他框架一样，包含 beforeAll()、beforeEach() 和类似的方法。阅读和遵循文档会对你有帮助。**

## 步骤 4：CI/CD 集成

下面是我为 GitHub Actions 准备的一个非常简单的 yaml 文件。这与其他方法一样，可以根据你的项目需求进行调整。我会给你一个简单的示例以供参考，剩下的就靠你了 :)

```yaml
name: API Test CI/CD

on:
push:
branches:

- main

jobs:
api_test:
runs-on: ubuntu-latest

steps:

- name: Checkout Repository
  uses: actions/checkout@v2

       - name: Setup Node.js
         uses: actions/setup-node@v2
         with:
           node-version: '14'

       - name: Install Dependencies
         run: npm install

       - name: Run API Tests
         run: npm test
```

这个 GitHub Actions 示例将在每次推送时运行 API 测试。你可以通过在 **.env** 文件中存储敏感的密码来提高安全性。

希望这对你有帮助。在本文中，我只是想谈谈如何使用它以及作为初学者你可以如何使用它。当然，你会有自己独特的方法和结构来建立项目。我建议你阅读 Playwright 文档。同时，TypeScript 也为我们提供了灵活性。你也可以使用不同的库。我可能会在下一篇文章中通过提供更多细节来扩展我的观点。

## 来源

[URL Source](https://numanhanduran.medium.com/can-we-use-playwright-for-api-automation-project-yes-9857865dedea)

发布时间: 2023-11-06
