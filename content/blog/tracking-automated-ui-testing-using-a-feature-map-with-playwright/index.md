+++
date = 2023-12-11
title = "使用 Playwright 的feature map框架改进 UI测试用例的可观测性"
description = "用feature map在代码里自动列出哪些功能已经被测试过了"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

几周前，[Ben Fellows](https://www.linkedin.com/in/ben-f-44778426/) 创建了一个 [LinkedIn 帖子](https://www.linkedin.com/posts/ben-f-44778426_as-a-qa-service-provider-building-automation-activity-7130958531586916352-qygv)，询问他在工作中经常遇到的问题的解决方案。

> 作为构建自动化的 QA 服务提供商，我面临的一个挑战是让客户看到并参与测试计划。我尝试过 TestPad、TestRail、Sheets，甚至是像 Jira 这样更项目导向的方法。有一段时间，我只是使用 Playwright 报告，但遭到了反对。有没有人认为有一个很好的解决方案可以让非技术参与者查看自动化的实时测试套件？

我回应了我的解决方案，利用 feature map(特性地图)来跟踪我的自动化进度。在本文中，我将演示如何将 [feature-map](https://www.npmjs.com/package/feature-map) npm 包实现到 [playwright-practicesoftwaretesting.com](https://github.com/playwrightsolutions/playwright-practicesoftwaretesting.com) 仓库中。特性地图最初是作为一个 Excel 电子表格开始的，在那里我跟踪系统的各个区域和我们想要用自动化覆盖的场景。从那里，[Sergei Gapanovich](https://playwrightsolutions.com/author/sergei/) 接受了这个想法，并编写了驱动 feature-map 包的代码。

## 概述：feature-map 包

feature-map 包是一个基本的库，它允许您创建一个包含网站内不同操作/特性的 yaml 文件，并添加一个 `true` 或 `false` 值以指示该特性是否有自动化覆盖。

这个工具的主要目的是创建一个通过 UI 可以在 web 应用程序中执行的所有不同操作的地图，并对其进行映射。基于此地图，我们可以指示是否有任何自动化覆盖来行使该功能，如果有，可以标记为 `true`。通过这种功能，我们可以跟踪我们正在测试的 UI 的整体测试覆盖率。我喜欢把它想象成一个测量棒。我们创建一个项目列表，然后我可以用它来衡量我或我的团队的测试覆盖率进度。

这个方法的好处是所有这些都可以通过 yaml 文件创建和维护，该文件也会提交到与您的测试代码相同的仓库中。因此，当您添加覆盖新操作的自动化覆盖时，您也可以更新 feature-map，并获得有关有多少特性有任何自动化覆盖的反馈。

你说的百分比是测试覆盖率百分比吗？嗯，某种程度上是。我知道有些人不喜欢讨论测试覆盖率或自动化覆盖率的百分比。当你真的思考它时，将这种未知的 [棘手问题](https://www.workroom-productions.com/wicked-problems/) 的绝对百分比放在一起是非常困难的。所以当我思考和讨论百分比时，它是确定我们想要衡量的事物（网站中的操作），将它们添加到 yaml 中，并衡量是否有任何覆盖这些操作的覆盖率。我对这种“自动化覆盖”和跟踪方式感到满意，就像我们正在构建的测量棒一样。

![Image 1](https://playwrightsolutions.com/content/images/2023/12/image-2.png)

👆 复古测量 📏

一旦我们开始实现 feature-map 包，我们的输出将如下所示。

![Image 2](https://playwrightsolutions.com/content/images/2023/12/image-1.png)

## 实现 feature-map 包

现在进入有趣的部分，下面您可以找到 npm 包的链接，其中包含关于如何将其实现到您自己的仓库中的详细说明。

[feature-map](https://www.npmjs.com/package/feature-map) 是手动跟踪项目中特性自动化覆盖进度的工具。

我们的第一步是将该包安装到我们的项目中，为此，请从目录的根目录运行以下命令。

```
npm install feature-map
```

下一步是在您的仓库中创建一个 yaml 文件，这将是我们的特性地图。我创建了一个名为 `featureMap.yml` 的文件，并开始构建我项目中的 UI 中发现的特性。

```yaml
- page: "/auth/login"
  features:
    sign in with google: false
    email: true
    password: true
    login: true
    register your account: false
    forgot password: false
- page: "/auth/forgot-password"
  features:
    email: false
    set new password: false
- page: "/auth/register"
  features:
    first name: false
    last name: false
    date of birth: false
    address: false
    postcode: false
    city: false
    state: false
    country: false
    phone rate: false
    e-mail address: false
    password: false
    register button: false
- page: "/category/hand-tools"
  features:
    header: true
    sidebar:
      sort: false
      filters: false
      by brand: false
    product card:
      image: false
      image zoom: false
      title: false
      price: false
    pagination:
      previous: false
      next: false
      number: false
- page: "/product/{id}"
  features:
    header: false
    product details:
      image: false
      title: false
      tags: false
      price: false
      description: false
      quantity: false
      add to cart: false
      add to favorites: false
    related products:
      image: false
      title: false
      more information: false
    footer: false
```

我们还没有在特性地图上列出网站内的所有操作，这将是一个待办事项，我们将在构建测试指标时继续构建。

在我们深入了解 yaml 文件是什么以及每个部分代表什么之前，有两个关键术语需要理解，以便完全理解 yaml 文件。我们将在 yaml 文件中使用 `Collections`。集合可以是：

- 序列（列表/数组）
- 映射（字典/散列）

首先，每当您看到短划线 (`-`) 时，它用于表示列表项或元素。因此，在最高层次上，我们使用这些序列（列表）来组织我们文件中的页面。

映射可以被认为是 yaml 文件中的键值对。

- `- page: "/auth/login"`：这行定义了一个新的 **列表**，URL 路径为 "/auth/login"。
- `features:` 这行开始一个与当前页面相关的 **特性** 列表。
- `sign in with google: false`：这行是一个 **映射** 示例，定义了一个名为 "sign in with google" 的特性/操作，并将其值设置为 `false`。

这种结构的好处是，您可以在页面内映射每个特性，甚至在需要时深入到多个弹出窗口，以便跟踪覆盖情况，重要的是每个列表（序列）都以键值对（映射）结束。

```yaml
# 有效
- page: "/category/hand-tools"
  features:
    header: true
    sidebar:
      sort: false
      filters: false
      by brand: false
    product_popup:
      additional details:
        high resolution image:
          download button: true

# 无效
- page: "/category/hand-tools"
  features:
    header: true
    sidebar:
      sort: false
      filters: false
      by brand: false
    product_popup:
      additional details:
        high resolution image:
          download button: # 注意这里没有列出键/值对
```

更多关于 yaml 文件格式的详细信息可以在下面找到！
[yaml 介绍](https://www.freecodecamp.org/news/what-is-yaml-the-yml-file-format/#yaml)
接下来，我们将介绍如何与 Playwright 集成。

## 与 Playwright 的集成

在 yaml 文件中创建特性列表后，下一步是更新我们的测试计划，以确保我们有覆盖这些特性的自动化测试，并更新 feature-map。

[playwright-practicesoftwaretesting.com](https://github.com/playwrightsolutions/playwright-practicesoftwaretesting.com) 仓库中有一个 [测试用例](https://github.com/playwrightsolutions/playwright-practicesoftwaretesting.com/blob/main/tests/registration.ts)，它覆盖了我们特性文件中的 `/auth/register` 页面，我们将确保更新我们的特性文件，并在项目中测试我们的 yaml 文件是否按预期工作。

```typescript
import { test, expect } from "@playwright/test";
import { featureMap } from "feature-map";

test.describe("My feature test", () => {
  test("Registration page - All fields and elements exist", async ({
    page,
  }) => {
    await page.goto("/auth/register");
    const yamlMap = featureMap("/path/to/your/yaml/file");

    await page.locator('input[name="first name"]').fill("John");
    yamlMap.set("/auth/register", "first name", true);

    await page.locator('input[name="last name"]').fill("Doe");
    yamlMap.set("/auth/register", "last name", true);

    // Similarly for other fields

    // Save updated map
    yamlMap.save();
  });
});
```

我们添加了一些指令来更新 `featureMap.yml` 文件中各个字段的值。添加字段并填写它们的内容时，将相应的 yaml 项目值更新为 `true`。

重要的是要记住，我们在特性映射文件中指定的每个元素和特性都必须在我们的自动化测试中得到适当的验证和覆盖。

您可能需要根据项目和测试套件的需求调整路径。

这就是我们实现特性地图以更好地跟踪自动化进度的方法。通过这种方法，我们可以在项目中创建一个交互式和透明的自动化覆盖地图。

## 结论

这个简单的工具和方法可以在更大程度上与您的团队和利益相关者一起工作，确保他们参与并了解 UI 测试的覆盖情况。这不仅可以提高自动化测试的质量，还可以确保项目中的所有关键功能都被覆盖。

## 来源

[来源](https://playwrightsolutions.com/tracking-automated-ui-testing-using-a-feature-map-with-playwright/)

发布时间: 2023-12-11
