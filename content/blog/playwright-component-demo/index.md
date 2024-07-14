+++
date = 2023-08-20
title = "如何使用组件来重构playwright的代码"
description = "独立了一个component层，提高代码的复用性"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

## playwright-component-demo

基于组件模型重写的 Playwright TodoMVC 应用演示测试测试用例

## 动机

页面对象模型（pom）是组织测试代码的推荐方法。然而,对于大型应用来说,许多元素在不同页面间保持不变,如导航栏、页眉和页脚。这不仅涉及相同的部分,还包括可复用的部分。

以表格为例。通常应用会有一个用于渲染表格内部组件,并在各处使用。因此,编写涉及表格的测试时,所需的逻辑基本上是一样的。许多情况下,应用还会有基于表格组件的复合组件,添加特定逻辑,如带搜索功能的用户表格或可排序的发票表格。

这种可可复用性和可组合性使得基于组件的模型成 web 前端开发的最佳方式。那么,为什么不在编写自动化测试用例时采用同样的方法呢?

## 实现

我们的核心思想是创建一个中间层的组件来抽象具体的 web 应用,所有测试都基于这些组件。TodoMVC 演示应用的组件可以在`tests/components`文件夹中找到。

一般情况下模版是这样的:

```javascript
export function Component (parent, options = {}) {
  const self = parent.locator(...); // 组件根节点的定位器
  const child = self.locator(...); // 过于简单而不需要单独成为组件的子元素
  const otherComponent = (options) => OtherComponent(self, options); // 子组件

  // 组件的操作隐藏了内部细节,不暴露具体使用哪个子元素或组件
  const someAction = () => child.click();
  const anotherAction = (param) => otherComponent({ param }).action();

  // 导出具体的API接口:
  return {
    someAction,
    anotherAction,
    expect: () => ({
      ...expect(locator), // 复制Playwright的所有标准断言
      toHaveCustomCondition: () => expect(child).toHaveClass(...) // 自定义断言以隐藏内部细节
   })
 };
}
```

在测试用例中的使用示例:

```javascript
test(async ({ page }) => {
  const component = Component(page);
  await component.expect().toBeVisible();
  await component.someAction();
  await component.expect().toHaveCustomCondition();
});
```

## 对比

以下是原始测试和更新后测试的几个对比:

#### 示例 1

```javascript
test("应该允许我将所有项目标记为已完成", async ({ page }) => {
  // 完成所有待办事项
  await page.getByLabel("全部标记为完成").check();

  // 确保所有待办事项都有'completed'类
  await expect(page.getByTestId("todo-item")).toHaveClass([
    "completed",
    "completed",
    "completed",
  ]);
  await checkNumberOfCompletedTodosInLocalStorage(page, 3);
});
```

对比

```javascript
test("应该允许我将所有项目标记为已完成", async ({ page }) => {
  // 完成所有待办事项
  await Header(page).completeAll();

  // 确保所有待办事项都有'completed'类
  await TodoList(page).expect().toHaveAllCompleted();
  await checkNumberOfCompletedTodosInLocalStorage(page, 3);
});
```

#### 示例 2

```javascript
test("当没有已完成的项目时应该隐藏", async ({ page }) => {
  await page.locator(".todo-list li .toggle").first().check();
  await page.getByRole("button", { name: "清除已完成" }).click();
  await expect(page.getByRole("button", { name: "清除已完成" })).toBeHidden();
});
```

对比

```javascript
test("当没有已完成的项目时应该隐藏", async ({ page }) => {
  await TodoList(page).todoAt(1).complete();
  const footer = Footer(page);
  await footer.clearCompleted();
  await footer.expect().toAllowClearCompleted(false);
});
```

#### 示例 3

```javascript
test("应该高亮当前应用的过滤器", async ({ page }) => {
  await expect(page.getByRole("link", { name: "全部" })).toHaveClass(
    "selected"
  );
  await page.getByRole("link", { name: "活动" }).click();
  // 页面变化 - 活动项目
  await expect(page.getByRole("link", { name: "活动" })).toHaveClass(
    "selected"
  );
  await page.getByRole("link", { name: "已完成" }).click();
  // 页面变化 - 已完成项目
  await expect(page.getByRole("link", { name: "已完成" })).toHaveClass(
    "selected"
  );
});
```

对比

```javascript
test("应该高亮当前应用的过滤器", async ({ page }) => {
  const footer = Footer(page);
  await footer.link("全部").expect().toBeSelected();
  await footer.selectLink("活动");
  // 页面变化 - 活动项目
  await footer.link("活动").expect().toBeSelected();
  await footer.selectLink("已完成");
  // 页面变化 - 已完成项目
  await footer.link("已完成").expect().toBeSelected();
});
```

## 来源

URL 来源: https://github.com/vangelov/playwright-component-demo
