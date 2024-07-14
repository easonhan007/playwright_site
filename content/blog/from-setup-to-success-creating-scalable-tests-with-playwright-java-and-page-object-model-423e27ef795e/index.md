+++
date = 2023-11-14
title = "使用playwright和java从0到1构建自动化测试框架"
description = "如何使用maven 和 page object来从零到一构建基于java的自动化测试框架"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译", "java"]
[extra]
math = false
image = "banner.jpg"
+++

## 引言

_拥抱现代网页自动化:Playwright 与 Java 以及页面对象模型_

## 网页自动化革新:Playwright 的崛起

在 web 开发中,自动化测试已成为不可或缺的一部分。Playwright 的出现标志着这一领域的重大进步。作为一个跨浏览器自动化库,Playwright 使开发人员和测试人员能够为网络应用程序编写可靠且强大的测试。它能够在真实环境下与多个浏览器(包括 Chrome、Firefox 和 Safari)交互,这一特性使其从前辈中脱颖而出。这种能力确保了在不同浏览环境中的全面覆盖和兼容性,这对当今多样化的 web 生态系统中至关重要。

你也可以查看[这篇文章对 Cypress 和 Playwright 进行了全面比较](https://medium.com/@mohsenny/deciding-between-cypress-and-playwright-a-comprehensive-guide-4d883d1be147),因为这两个自动化框架目前都被广泛使用,处于领先地位。

## Java 与 Playwright:强大的组合

Java 以其稳定性、可扩展性和强大的生态系统而闻名,是实现基于 Playwright 的测试自动化的绝佳选择。Java 丰富的库、强大的社区支持和跨平台特性使其成为许多组织的首选语言。当与 Playwright 的功能相结合时,Java 提供了一个强大的框架,用于创建复杂而高效的自动化测试套件。

## 引入页面对象模型(POM)以实现可维护的测试自动化

页面对象模型(POM)是一种设计模式,已成为现代测试自动化策略的基石。POM 提倡为每个网页创建单独的对象,封装页面的结构和行为。这种分离带来了诸多好处:

1. **增强可维护性:** 网络应用程序 UI 的变化可以通过更新页面对象来管理,最大限度地减少测试脚本的变动。
2. **提高可读性:** 测试脚本变得更易读懂,因为它们使用反映用户操作的方法,而不是直接与 UI 元素交互。
3. **可复用性:** 页面对象可以在不同的测试中重复使用,减少代码重复。
4. **改善协作:** 清晰的结构使团队更容易理解和贡献测试代码,增强协作。

## 探索 Playwright 的录制回放工具

在设置好 Playwright 后,你应该探索的第一个功能之一是 Playwright 的代码生成工具,通常被称为"codegen"。Codegen 是一个革命性的功能,它通过记录你与网络应用程序的交互并生成相应的 Playwright 代码来协助创建测试脚本。

## Codegen 的优势:

- **快速脚本创建:** 它显著加快了编写测试脚本的过程,特别是对于复杂的交互。
- **学习工具:** 对于 Playwright 新手来说,它是一个出色的学习辅助工具,展示了 Playwright 脚本的结构。
- **准确性:** 有助于捕获精确的选择器,减少手动编写选择器时可能出现的错误。

## 使用 Codegen:

要使用 codegen,可以在命令行中以 codegen 模式运行 Playwright。这将打开一个浏览器,你可以在其中手动执行你希望自动化的操作。Playwright 将记录这些操作并实时生成相应的代码。以下是启动 codegen 的简单示例:

```bash
npx playwright codegen example.com
```

这个命令会启动一个浏览器窗口,你可以在其中与"example.com"进行交互。当你浏览和与网站互动时,Playwright 会为这些操作生成代码:

![图片 3](https://miro.medium.com/v2/resize:fit:700/1*wbhbuGRovWEGyW-434juJg.png)

## 与 POM 集成:

尽管 codegen 是一个强大的工具,但将生成的代码集成到页面对象模型结构中以保持可维护性是至关重要的。使用生成的代码作为基础,并对其进行完善以适应你的页面类和测试结构。

在接下来的章节中,我们将深入探讨如何使用 Java 设置 Playwright 项目,利用页面对象模型创建一个健壮、可维护和可扩展的自动化框架。

要查看这些概念的实际应用并获取本文中 Google 搜索示例的完整代码,请随时查看这个综合性仓库:[PlaywrightWithJava](https://github.com/mohsenny/PlaywrightWithJava)。它作为一个即用型模板,用于使用页面对象模型实现 Java 的 Playwright 测试。

## 第一章: Playwright 和 Java 入门

_奠定基础:设置 Java、Maven 和 Playwright_

在本章中,我们将指导你完成使用 Java 和 Maven 设置 Playwright 项目的初始步骤。这个设置是创建高效且可扩展的 web 自动化框架的第一步。

### 1. 初始化 Java 和 Maven 环境:

在深入 Playwright 之前,确保你的系统上已安装 Java 和 Maven。Java 是你将使用的编程语言,而 Maven 是一个强大的构建工具,简化了依赖管理和项目构建。

- 安装 Java: 你需要在系统上安装 Java JDK。你可以从 [Oracle 网站](https://www.oracle.com/java/technologies/javase-jdk11-downloads.html)下载,或使用 OpenJDK。
- 安装 Maven: 从 [Apache Maven 项目](https://maven.apache.org/download.cgi)下载并安装 Maven。按照他们网站上提供的安装说明在你的系统上设置它。

### 2. 安装 Java 版 Playwright:

一旦 Java 和 Maven 设置完成,下一步是将 Playwright 添加到你的项目中。你可以通过在 Maven 项目中添加 Playwright 作为依赖项来实现这一点。

- **创建新的 Maven 项目:** 如果你正在开始一个新项目,在你喜欢的 IDE 中或从命令行创建一个 Maven 项目。
- **添加 Playwright 依赖:** 在你的 `pom.xml` 中,添加以下依赖项以包含 Playwright:

```xml
<dependencies>
    <!-- Playwright -->
    <dependency>
        <groupId>com.microsoft.playwright</groupId>
        <artifactId>playwright</artifactId>
        <version>[latest_version]</version>
        <scope>test</scope>
    </dependency>
    <!-- 测试运行器和断言 -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>RELEASE</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.13.2</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.junit</groupId>
        <artifactId>junit-bom</artifactId>
        <version>5.10.1</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
    <!-- 根据需要添加其他依赖 -->
</dependencies>
```

- 将 `[latest_version]` 替换为 Java 版 Playwright 的最新版本,你可以在 [Maven 仓库](https://mvnrepository.com/artifact/com.microsoft.playwright/playwright)上找到。

### 3. 验证配置:

在设置完项目并添加 Playwright 依赖后,至关重要的是验证一切是否正常运行。

- **创建一个简单的测试:** 编写一个小脚本来打开浏览器并导航到一个网页。这里是一个例子:

```java
package com.example;

import com.microsoft.playwright.*;

public class TestExample {
    public static void main(String[] args) {
        try (Playwright playwright = Playwright.create()) {
            Browser browser = playwright.chromium().launch();
            Page page = browser.newPage();
            page.navigate("https://example.com");
            System.out.println(page.title());
        }
    }
}
```

- **运行你的测试:** 使用 Maven 执行这个脚本,以确保 Playwright 可以启动浏览器并执行操作。

随着 Java、Maven 和 Playwright 的成功设置,你现在已准备好深入 web 自动化测试的世界。接下来的章节将涵盖你的项目结构以及如何有效地实现页面对象模型以进行可维护和可扩展的测试。

## 第二章: 可维护性的项目结构

_构建你的测试框架:使用 Java 和 Maven 的最佳项目布局_

创建一个组织良好的项目结构对于维护一个可扩展和高效的自动化框架至关重要。本章概述了使用 Java 和 Maven 的 Playwright 项目的最佳实践,强调可维护性和易用性。

### 1. 推荐的目录结构:

结构化的方法有助于有效管理代码,尤其是随着项目的增长。以下是推荐的项目结构:

```bash
YourProject
├── src
│   ├── main
│   │   ├── java
│   │   │   └── com
│   │   │       ├── pages
│   │   │       └── utils
│   │   └── resources
│   │       └── translations
│   └── test
│       ├── java/
│       │   └── com
│       │       └── tests
│       └── resources
│           ├── config
│           └── utils
└── pom.xml
```

- `src/main/java`: 包含测试框架的核心,包括页面对象和实用工具类。
- `src/test/java`: 存放测试脚本,以反映应用程序结构的方式组织。
- `src/test/resources`: 存储外部资源,如选择器和测试数据,将它们与测试逻辑分开。

### 2. 每个组件的说明:

- **页面类** (`src/main/java/.../pages/`): 应用程序中的每个网页都应该有一个对应的页面类。这个类封装了网页的所有功能,遵循页面对象模型。
- **实用工具类** (`src/main/java/.../utils/`): 这些类可以包括各种实用工具,如配置读取器、常见任务的辅助方法等。
- **测试类** (`src/test/java/.../tests/`): 在这里,你编写实际的测试用例,使用页面类。
- **测试数据文件** (`src/test/resources/testdata/`): 将你的测试数据(如用户名和密码)保存在外部文件中,以便于管理并避免硬编码。
- **Maven 配置** (`pom.xml`): 这个文件管理项目依赖、插件和其他配置。

### 3. 页面类的例子:

以下是一个简单的页面类示例,代表登录页面:

```java
package com.yourcompany.yourproject.pages;

import com.microsoft.playwright.Page;

public class LoginPage {
    private final Page page;

    // 定位器
    private final String USERNAME_INPUT = "#username";
    private final String PASSWORD_INPUT = "#password";
    private final String LOGIN_BUTTON = "#login";

    public LoginPage(Page page) {
        this.page = page;
    }

    public void login(String username, String password) {
        page.fill(USERNAME_INPUT, username);
        page.fill(PASSWORD_INPUT, password);
        page.click(LOGIN_BUTTON);
    }
}
```

一个结构良好的项目布局对于测试框架的长期可维护性和可扩展性至关重要。通过将代码组织成逻辑部分并将选择器和测试数据外部化,你为测试自动化工作创建了一个强大的基础。在下一章中,我们将深入探讨如何创建有效且可维护的页面类。

## 第三章: 创建页面类

_构建强大的页面对象:Playwright 中页面类构建指南_

使用页面对象模型(POM)的可维护测试自动化框架的关键组成部分之一是创建页面类。本章重点介绍如何使用 Playwright 和 Java 有效构建这些类。

### 1. 页面类在 POM 中的角色:

页面类作为网页 UI 元素的接口。每个页面类对应应用程序中的一个页面,封装了可以在该页面上执行的操作。这种方法提高了可维护性，优化了可读性,并减少了代码重复。

## 2. 构建页面类:

以下是创建页面类的分步指南:

- **识别 UI 元素:** 确定网页上测试将与之交互的所有元素,如文本框、按钮和链接。
- **定义选择器:** 在页面类中存储这些元素的选择器。最佳做法是将这些选择器外部化,但为简单起见,我们将直接在类中定义它们。
- **实现操作:** 为页面上可以执行的每个操作创建方法,如输入文本、点击按钮等。

### 3. 示例:创建 SearchPage 类:

让我们为 Google 搜索页面创建一个 `SearchPage` 类:

```java
package org.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;
import org.util.TranslationReader;

public class SearchPage {
    private final Page page;
    /* 为避免硬编码文本,我们从翻译文件中读取它们
       以便在定义选择器时使用。
       你可以在这里查看 TranslationReader.java 的内容:
       https://shorturl.at/vRST3 */
    TranslationReader reader = new TranslationReader();

    public SearchPage(Page page) {
        this.page = page;
    }

    // 选择器:返回页面某些元素的选择器
    public Locator getCookieSelector() {
        return page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName(
                reader.getTranslation("cookie.accept")
        ));
    }

    public Locator getSearchField() {
        return page.getByRole(AriaRole.COMBOBOX, new Page.GetByRoleOptions().setName(
                reader.getTranslation("search")
        ));
    }

    /* ...更多选择器 */

    // 方法:在页面上执行特定操作
    public void clickCookieAcceptButton(){
        getCookieSelector().click();
    }

    public void performSearch(String searchKeyword) {
        getMainSearchField().fill(searchKeyword);
        getSearchButton().click();
    }
    /* ...更多方法 */
}
```

在这个例子中,`SearchPage` 类代表我们登陆 Google 时的第一个页面。它包括与页面交互的方法,如使用给定关键词搜索和导航到不同的结果标签。

### 4. 设计页面类的最佳实践:

- **每个页面一个类:** 为应用程序的每个页面创建一个单独的类。
- **描述性方法名:** 使用清晰描述操作的名称,如 `performSearch()` 或 `navigateToImageResults()`。
- **模块化:** 设计你的方法使其小巧、专注且可以复用。

页面类是使用 Playwright 和 Java 构建可扩展和可维护的测试自动化框架的基础。通过封装与网页的交互,你创建了一个强大且可复用的结构,简化了测试脚本并使其更能适应 UI 的变化。

## 第四章:编写测试类

_实现有效的测试用例:在测试中集成页面对象_

在设置好页面类之后,下一步是编写测试类。这些脚本将使用页面类中定义的方法与网络应用程序进行交互。本章介绍如何使用 Playwright 和 Java 创建这些测试用例。

### 1. 编写测试类的基础:

测试类应该清晰、简洁,并专注于测试逻辑,而不是与网络应用程序交互的细节。这些测试将使用页面类提供的方法。

### 2. 构建测试类:

一个典型的测试类包括:

- **setup 方法:** 在每个测试之前初始化 Playwright 浏览器和其他先决条件。
- **测试方法:** 单独的测试用例,每个代表不同的场景。
- **清理方法:** 在每个测试之后关闭浏览器并执行任何清理。

### 3. 利用 `PlaywrightExtension` 实现高效的测试设置和清理

在自动化测试领域,效率和可复用性至关重要。这就是 `PlaywrightExtension` 发挥作用的地方,它是一个自定义的 JUnit 扩展,旨在简化测试的 setup 和 teardown 过程。`PlaywrightExtension` 显著减少了样板代码,确保每个测试类都遵循 DRY(不要重复自己)原则。

_什么是 **PlaywrightExtension**?_

`PlaywrightExtension` 是一个自定义的 JUnit 扩展,用于自动化每个测试的 Playwright 资源的初始化和清理。它管理浏览器实例、页面和上下文的生命周期,确保每个测试都从一个干净的状态开始。这种方法消除了在每个测试类中重复设置和清理代码的需要,使你的测试更清晰、更易于维护。

要实现 `PlaywrightExtension`,将其定义为 JUnit 5 扩展,并用 `@ExtendWith(PlaywrightExtension.class)` 注解你的测试类。这告诉 JUnit 使用 `PlaywrightExtension` 中定义的方法来管理测试环境。

```java
import org.junit.jupiter.api.extension.ExtendWith;
import com.microsoft.playwright.*;

@ExtendWith(PlaywrightExtension.class)
public class YourTest {
    // 测试方法在这里
}
```

`PlaywrightExtension` 类本身看起来像这样:

```java
package resources.config;

import java.nio.file.Paths;
import com.microsoft.playwright.*;
import org.junit.jupiter.api.extension.*;

public class PlaywrightExtension implements BeforeEachCallback, AfterEachCallback {
    private static Browser browser;
    private static BrowserContext context;
    private static Page page;

    @Override
    public void beforeEach(ExtensionContext context) throws Exception {
        // 覆盖并全局定义 beforeEach
    }

    @Override
    public void afterEach(ExtensionContext context) throws Exception {
        // 覆盖并全局定义 afterEach
    }

    public static Page getPage() {
        return page;
    }

    public static Browser getBrowser() {
        return browser;
    }
}
```

这样我们可以实现以下目标:

1. **减少样板代码:** 自动处理常见的设置和清理任务。
2. **一致性:** 为每个测试用例确保一致的测试环境。
3. **资源管理:** 高效管理和处理 Playwright 资源,防止资源泄漏。
4. **增强可读性:** 简化测试类,使其更易读和维护。

在现有的测试类中,你可以用 `PlaywrightExtension` 替换原本用于设置和清理的 `@BeforeEach` 和 `@AfterEach`。以下是修订后的测试类示例:

```java
package org;

import com.microsoft.playwright.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.pages.SearchPage;

@ExtendWith(PlaywrightExtension.class)
public class SearchTests {
    static Browser browser;
    static SearchPage searchPage;
    static Page page;

    @BeforeEach
    public void createContextAndPage() {
        // 这里你可以从 PlaywrightExtension 访问页面
        page = PlaywrightExtension.getPage();
        page.navigate("https://www.google.com");
    }

    @Test
    public void shouldSearch() {
        // 使用 SearchPage 的测试实现
    }

    @AfterAll
    public static void tearDown() {
        page.close();
        // 这里你可以从 PlaywrightExtension 访问浏览器
        PlaywrightExtension.getBrowser().close();
    }
}
```

在这个例子中,`PlaywrightExtension` 处理 `Page` 和 `Browser` 实例的创建和关闭,从而简化了测试结构。

### 4. 示例:创建搜索测试类:

让我们创建一个 `SearchTest` 类,使用 `SearchPage` 类测试 Google 的搜索功能:

```java
package org;

import com.microsoft.playwright.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.pages.SearchPage;
import resources.config.PlaywrightExtension;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

@ExtendWith(PlaywrightExtension.class)
public class SearchTests {
    static Browser browser;
    static SearchPage searchPage;
    static Page page;

    @BeforeEach
    public void createContextAndPage() {
        page = PlaywrightExtension.getPage();
        searchPage = new SearchPage(page);
        page.navigate("https://www.google.com");
    }

    @Test
    public void shouldSearch() {
        searchPage.clickCookieAcceptButton();
        searchPage.performSearch("Potato");
        assertThat(searchPage.getSearchField()).containsText("Potato");
        searchPage.navigateToImageResults();
        // 更多断言...
        searchPage.navigateToAllResults();
        searchPage.navigateToVideoResults();
        // 更多断言...
    }

    @AfterAll
    public static void tearDown() {
        page.close();
        PlaywrightExtension.getBrowser().close();
    }
}
```

在这个例子中,`shouldSearch` 是一个使用 `SearchPage` 执行 Google 搜索的测试方法。它展示了如何使用页面对象使测试逻辑变得更加可读和简洁。

### 5. 实现清晰可读的测试代码的技巧

- **描述性测试名称:** 为测试方法使用有意义的名称,描述测试验证的内容。
- **模块化测试:** 编写小型、专注的测试,每次验证应用程序的一个功能。
- **可复用的 setup 和 teardown:** 使用 `@BeforeEach` 和 `@AfterEach` 注解处理常见的设置和清理任务。
- **断言:** 包含断言以验证测试的结果,确保它们检查正确的条件。

测试类是将页面类的功能整合在一起以与应用程序交互的地方。通过遵循这些指南,你可以创建不仅有效捕获 bug,而且易于阅读和维护的测试。

最后,为了展示到目前为止项目结构的样子:

![图片 4](https://miro.medium.com/v2/resize:fit:490/1*XVyB7XWls68tWItwqhJuhA.png)

Google 搜索测试的项目结构

## 第五章:外部化选择器和测试数据

_增强测试灵活性和维护性:管理选择器和测试数据的策略_

在维护一个强大且适应性强的测试自动化框架中,高效管理选择器和测试数据至关重要。本章探讨如何在 Playwright 项目中外部化选择器和测试数据,提高灵活性并减少频繁更改代码的需求。

### 1. 外部化选择器的重要性:

在测试脚本或页面类中硬编码选择器可能导致维护噩梦,尤其是当 UI 发生变化时。通过外部化这些选择器,你可以轻松更新它们,而无需更改核心测试逻辑。

### 2. 使用 JSON 进行选择器管理:

管理选择器的一种有效方法是将它们存储在 JSON 文件中。这允许你更改选择器而无需触及 Java 代码。以下是一个例子:

**乙醇的注释 👀：这个方法我既不喜欢也不推荐。对于 java 代码来说，直接在 pom 里修改定位器是有代码提示的，比独立出来写 json 文件要好一点**

- **JSON 选择器文件** (`loginSelectors.json`):

```json
{
  "usernameInput": "#username",
  "passwordInput": "#password",
  "loginButton": "#login"
}
```

- **在页面类中读取选择器:** 修改你的页面类以从这些 JSON 文件读取选择器。你可以使用 Java 的内置库或第三方库如 Jackson 或 Gson 来解析 JSON 文件。

### 3. 外部化测试数据:

与选择器类似,测试数据如用户名、密码或任何输入数据也应该外部化。这种做法不仅使你的测试更易读,还简化了数据管理并增强了安全性。

- **JSON 测试数据文件** (`loginTestData.json`):

```json
{
  "validUser": {
    "username": "user1",
    "password": "pass123"
  },
  "invalidUser": {
    "username": "user2",
    "password": "wrongpass"
  }
}
```

- **在测试中使用测试数据:** 在测试类中加载这些数据,并用它来驱动你的测试。这种方法对于数据驱动测试特别有用。

## 4. 选择器和测试数据管理的最佳实践:

- **保持组织:** 以有组织的方式存储你的选择器和测试数据,最好在项目内的专用目录中。
- **版本控制:** 将这些 JSON 文件包含在你的版本控制系统中,以跟踪更改并维护更新历史。
- **安全考虑:** 对敏感数据要谨慎。对于高度敏感的数据(如真实密码),使用环境变量或安全保管库。

外部化选择器和测试数据增强了测试自动化框架的可维护性和可扩展性。它允许更容易地更新和修改,使你的测试对应用程序 UI 和数据集的变化更具弹性。

## 结论

_拥抱自动化测试的未来:关键要点和下一步_

如果你想深入了解并查看完整设置,我准备的 [PlaywrightWithJava](https://github.com/mohsenny/PlaywrightWithJava) 仓库提供了一个全面的示例,展示了本文讨论的概念。

在结束我们关于使用页面对象模型设置 Playwright 与 Java 的指南时,重要的是回顾关键要点 并进行讨论下一步行动。

### 1. 关键点回顾:

- **Playwright 和 Java:** 我们探索了 Playwright 与 Java 的强大组合,突出了这对组合在自动化测试中的优势。
- **项目结构:** 讨论了最佳的项目布局,强调了可维护性和组织性。
- **页面对象模型(POM):** 概述了 POM 的实现,展示了它在创建可扩展和可维护的测试脚本中的重要性。
- **页面类:** 我们深入研究了页面类的创建,这是 POM 的核心组件,并提供了说明其结构和功能的示例。
- **测试类:** 涵盖了编写有效测试类的结构和最佳实践,确保测试的清晰性和高效。
- **外部化选择器和数据:** 强调了外部化选择器和测试数据的重要性,突出其在增强测试灵活性和可维护性方面的作用。

### 2. 鼓励探索和适应:

web 自动化的世界广阔且不断发展。虽然本指南提供了坚实的基础,但继续探索和适应至关重要。请持续关注 Playwright、Java 和测试自动化的最新发展。尝试不同的方法和工具,找出最适合你特定需求的方式。

## 3. 社区和持续学习:

与社区互动是无价的。参与论坛、参加网络研讨会,并为开源项目做贡献。这种互动促进学习,可以让你了解行业的最佳实践。

## 4. 下一步:

- **集成高级功能**: 探索 Playwright 和 Java 的高级功能,如处理动态内容、使用 iframe 等。
- **CI/CD 集成:** 考虑将你的测试集成到 CI/CD 流程中,实现自动化测试执行。
- **性能和安全测试:** 扩展你的测试范围,包括性能和安全方面。

## 5. 最后思考:

自动化测试是一个持续学习和改进的旅程。本指南中讨论的设置和实践只是开始。拥抱自动化测试带来的挑战和机遇,你将为 web 自动化的质量和成功做出重大贡献。

## 来源

[URL Source](https://medium.com/@mohsenny/from-setup-to-success-creating-scalable-tests-with-playwright-java-and-page-object-model-423e27ef795e)

发布时间: 2023-11-14
