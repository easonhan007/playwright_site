+++
date = 2025-01-22
title = "Playwright自动化中的动态页面对象类加载"
description = "https://medium.com/@thananjayan1988/optimizing-playwright-tests-with-dynamic-page-object-loading-dfda67be81e4"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

### 动态类加载

页面对象模型（**POM**）是 UI 测试自动化中最常用的设计模式之一。它在组织测试脚本、增强可维护性和促进可重用性方面非常有效。在深入探讨这个话题之前，我们先讨论一个实际用例，以了解其优势。

#### 场景：电子商务网站测试

假设你正在为一个电子商务网站项目工作。客户有一个独特的需求：同一套测试脚本应该在多个本地化站点上执行。乍一看，这似乎很简单且易于实现。但等等……真的是这样吗？

让我们探讨一些可能的方法来满足这一需求：

- **维护独立分支**  
  为每个本地化站点编写独立的脚本，并在 Git 中为每个地区维护不同的分支。
- **在页面对象类中使用条件方法**  
  在页面对象类中定义方法，通过条件逻辑处理本地化，例如：

```javascript
if (localization === 'en') {
   // 英文代码 }
else {
   // 其他语言代码
}
```

**使用 OR 条件的动态定位器**

创建支持多种本地化需求的 Playwright 定位器，使用[OR](https://playwright.dev/docs/api/class-locator#locator-or)条件匹配多个元素。

这些方法中的每一种都可能满足当前的需求。然而，当你退一步考虑更大的图景时——考虑到添加更多测试场景、支持更多本地化、维护代码库以及与其他服务集成等参数——你可能会注意到显著的缺点。

- **代码重复**：每个本地化的独立分支导致代码重复。
- **复杂性**：随着应用程序的扩展，条件逻辑变得难以管理。
- **可维护性差**：添加新的本地化或更新现有脚本需要大量工作，使框架变得笨重。

为了解决这些挑战，你可以利用**装饰器**、**反射**或**动态类加载**等高级概念。这些技术允许你的测试框架根据本地化设置动态引用不同的页面对象类，从而减少重复并增强灵活性。

在本演示中，我们将重点介绍**动态类加载**，展示相同的测试脚本如何在多个本地化站点上无缝工作。

### 动态类加载：本地化站点的解决方案

动态类加载允许你根据本地化语言在运行时加载适当的页面对象类。

**_注意_**：为了简单起见，我将保持示例代码简洁并专注于概念。在实际项目中实现时，请确保遵循所有 POM 最佳实践，并避免在页面对象方法中硬编码数据。

首先，我们需要通过在控制台中执行 JavaScript 代码来识别网页的本地化设置。

```javascript
const pageLanguage = await page.evaluate(() => document.documentElement.lang || "Not set");
console.log(pageLanguage)
# 输出 'en' 或 'de'
```

其次，为每个站点创建独立的页面对象类。我们创建一个接口类来定义方法，这将帮助你在代码补全和类型检查时使用。

```javascript
export default interface PomTemplate {
     searchAnItem(item:string):Promise<void>
     waitToOpenInNewTab():Promise<void>
     buyItNow():Promise<void>
     enterShippingAddressAndSubmit({}):Promise<void>
}
```

为英文本地化区域创建一个页面对象类。

```javascript
export default class EnLocalisedRegion implements PomTemplate {
    readonly page:Page
    private newPage: Page

    constructor(page:Page){
        this.page = page
    }

    async searchAnItem(item:string){
        await this.page.goto('/')
        await this.page.getByPlaceholder('Search for anything').fill(item)
        await this.page.getByPlaceholder('Search for anything').press('Enter')
        await expect(this.page.getByRole('heading', { name: '+ results for '+item })).toBeVisible()
    }

    async clickAnyItem(){
        await this.page.getByRole('link', { name: 'New Listing Pair of Vintage' }).click();
    }
    async waitToOpenInNewTab(){
       const [ page1 ] = await Promise.all([
            this.page.waitForEvent('popup'),
            this.page.getByRole('link', { name: 'Mattel JAL Uniform Barbie doll Japan Airlines Stewardess Flight Attendant Opens' }).click()
        ])
        this.newPage = page1
        await this.newPage.bringToFront()
    }

    async buyItNow(){
        await this.newPage.getByRole('link', { name: 'Buy It Now' }).click();
        await this.newPage.getByRole('link', { name: 'Check out as guest' }).click();
    }

    async enterShippingAddressAndSubmit(data:{}){
        await this.newPage.getByLabel('First name').fill('Thanan');
        await this.newPage.getByLabel('Last name').fill('Rahase');
        await this.newPage.getByLabel('Street address', { exact: true }).fill('Kamraj road perumal perr');
        await this.newPage.getByLabel('City').fill('Chennai');
        await this.newPage.getByLabel('State/Province/Region').selectOption('TN');
        await this.newPage.getByLabel('Email', { exact: true }).fill('test@gmail.com');
        await this.newPage.getByLabel('Confirm email').fill('test@gmail.com');
        await this.newPage.getByLabel('Phone number (required)').fill('8765423891');
        await this.newPage.locator('[data-test-id="ADD_ADDRESS_SUBMIT"]').click();
    }
}
```

为德文本地化区域创建一个页面对象类。

```javascript
export default class DeLocalisedRegion implements PomTemplate{
    readonly page:Page
    private newPage: Page

    constructor(page:Page){
        this.page = page
    }

    async searchAnItem(item:string){
        await this.page.goto('/')
        await this.page.getByPlaceholder('Bei eBay finden').fill(item)
        await this.page.getByPlaceholder('Bei eBay finden').press('Enter')
        await expect(this.page.getByText(`+ Ergebnisse für ${item}`)).toBeVisible()
    }

    async waitToOpenInNewTab(){
       const [ page1 ] = await Promise.all([
            this.page.context().waitForEvent('page'),
            this.page.getByRole('link', { name: 'Sparkle Beach Barbie Puppe' }).click()
        ])
        this.newPage = page1
        await this.newPage.bringToFront()
    }

    async buyItNow(){
        await this.newPage.getByRole('link', { name: 'Sofort-Kaufen' }).click();
        await this.newPage.getByRole('link', { name: 'Als Gast kaufen' }).click();
    }

    async enterShippingAddressAndSubmit(data:{}){
        await this.newPage.getByLabel('Vorname').fill('Thanan');
        await this.newPage.getByLabel('Nachname').fill('Rahase');
        await this.newPage.getByLabel('Straße und Hausnummer').pressSequentially('2812');
        const addrDisplay = this.newPage.locator('.auto-address-cntr')
        await expect(addrDisplay).toBeVisible()
        await addrDisplay.locator('div').first().click()
        await this.newPage.getByLabel('E-Mail', { exact: true }).fill('test@gmail.com');
        await this.newPage.getByLabel('E-Mail bestätigen').fill('test@gmail.com');
        await this.newPage.getByLabel('Telefon (erforderlich)').fill('09852 34578');
        await this.newPage.locator('[data-test-id="ADD_ADDRESS_SUBMIT"]').click();
    }
}
```

在我的 Playwright 测试中，我使用 fixture 来处理所有页面对象类实例的创建。

```javascript
import { test as PageFixture, expect } from '@playwright/test'
import  PomTemplate  from '../pages/pomTemplate'

type Pages = {
    [key: string]: PomTemplate
}

const test = PageFixture.extend< Pages >({

    dynamicPage: [ async({ page, baseURL }, use)=>{
        await page.goto(baseURL as string)
        //获取网站语言信息
        const pageLanguage = await page.evaluate(() => document.documentElement.lang || "Not set");
        const flowPage = await loadclass( pageLanguage, [page])
        await use(flowPage)
    }, { scope: 'test'}],
})

const loadclass =async (lang: string, args: any[])=>{
        const module = await import(`./../pages/${lang}_flow.page`);
        const newClass:{ new (...args:any[]):PomTemplate} = module.default;
        return new newClass(...args);
}

export { test, expect }
```

代码非常简单且易于理解，我将这些页面对象类保存在一个单独的`pages`文件夹中。在运行时，这些类模块会以懒加载的方式加载，并实例化相应的对象以供测试方法使用。现在看看你的测试方法。

```javascript
import { test } from './../init/pageFixture'

test.describe('Dynamic loading of class files', () => {
    test('eBay - Add address flow', async ({ dynamicPage }) => {
        await dynamicPage.searchAnItem('Barbie Doll')
        await dynamicPage.waitToOpenInNewTab()
        await dynamicPage.buyItNow()
        await dynamicPage.enterShippingAddressAndSubmit({})
    })
}
```

现在将`baseURL`设置为`https://ebay.com`或`https://ebay.de`，在执行时你可以清楚地看到正确的类被加载，脚本成功执行。

但请注意，动态加载需要仔细设计以确保正确的类型推断或显式类型转换。确保在运行时抛出任何错误时进行健壮的错误处理。

所有源代码可以在这里找到。

### 结论

动态类加载适用于需要灵活性和运行时适应性的场景。我们可以轻松地封装和解耦代码，以实现更好的设计和维护目的。
