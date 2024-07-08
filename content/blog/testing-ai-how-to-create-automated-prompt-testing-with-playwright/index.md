+++
date = 2024-07-08
title = "如何使用 Playwright 进行LLM的提示词注入测试"
description = "作者用 playwright 调用 llm 的 api，然后实现了一些断言，用来检查 llm 是否存在注入的问题"
authors = ["乙醇"]
[taxonomies]
tags = ["playwright进阶", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

## 我翻译的好痛苦 😂 写在前面

这篇文章一开始看的我云山雾绕，后来我看了一下[作者的代码](https://github.com/stuart-thomas-zoopla/LlmTestingWithPlaywright/tree/main/tests)，大概用一句话总结就是：作者用 playwright 调用 llm 的 api，然后实现了一些断言，用来检查 llm 是否存在注入的问题。

也就是说：**不用 playwright，用其他的测试框架去测试也是没问题的。**

---

欢迎来到我的 AI 测试系列的第二篇文章。本系列文章的灵感来源于 **[Ministry of Testing 30 天 AI 测试活动](https://www.ministryoftesting.com/events/30-days-of-ai-in-testing)**。如果您还没有阅读系列的第一篇文章，请查看 – [**测试 AI – 如何在本地运行 Llama 2 LLM**](https://www.thequalityduck.co.uk/testing-ai-how-to-run-the-llama-2-large-language-model-locally/)。在本文中，我将讨论如何使用 Playwright 为大型语言模型 (LLM) 创建自动化提示测试框架。

## 使用 Playwright 自动化 LLM 测试

在我写完 **[上篇文章](https://www.thequalityduck.co.uk/testing-ai-how-to-run-the-llama-2-large-language-model-locally/)** 后，我已经在本地运行了一个 LLM。接下来的问题是如何编写自动化测试？答案是使用 Playwright 进行提示测试。

### 什么是提示测试？

提示测试，有时称为提示工程，是向 LLM 提供提示并评估其响应的过程。在本文中，我不会详细讨论提示测试的细节，而是专注于如何创建可靠的自动化测试。

### 自动化提示测试工具

在本文中，我将使用以下工具：

- **[LLama 2](https://llama.meta.com/llama2/)** – 由 Meta 创建的大型语言模型
- **[Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md)** – 用于本地运行 Llama 2 的工具
- **[Playwright](https://playwright.dev/)** – 支持多种语言的测试框架

Ollama 提供了一个用于与 LLM 交互的 API，这使得创建自动化提示测试变得简单。

对于测试，我选择使用 TypeScript 编写。我在 **[GitHub](https://github.com/stuart-thomas-zoopla/LlmTestingWithPlaywright)** 上提供了我的示例测试框架。

虽然我们在进行 API 调用，但提示测试与 API 测试有显著区别。

### 提示测试与 API 测试的区别

使用 API 进行测试使得 LLM 测试与其他 API 测试非常相似，但有一个关键区别。我们永远不能百分之百确定从 LLM 接收到的响应。为了解决这个问题，我们必须编写基于期望响应中包含的关键字或短语的断言，而不是对完整响应进行断言。我有一些关于如何改进这方面的方法 – [**稍后会详细介绍**](https://www.thequalityduck.co.uk/testing-ai-how-to-create-automated-prompt-testing-with-playwright/#improving "稍后会详细介绍")。

### “禁止词”

我还尝试了一种“禁止词”的概念。这些是任何回复中都不应该包含的词，并且在所有测试中都要断言它们不在响应中。

根据 LLM 部署的上下文，这种用例会有所不同。我假设 LLM 是一个面向公众的服务。在这种情况下，有很多事情是您希望聊天机器人不要说的。从使用攻击性语言到评论竞争对手等。我们可以在所有测试中进行断言，并创建专门测试 **[提示注入](https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/Prompt_Injection.html)** 的测试。

### 什么是 LLM 的提示注入

**描述:** 提示注入涉及使用精心制作的提示绕过过滤器或操纵 LLM,使模型忽略先前的指令或执行非预期的操作。这些漏洞可能导致意外后果,包括数据泄露、未授权访问或其他安全漏洞。

**常见的提示注入漏洞:**

- 制作能够操纵 LLM 泄露敏感信息的提示。
- 通过使用特定的语言模式或标记绕过过滤器或限制。
- 利用 LLM 的分词或编码机制中的弱点。
- 通过提供误导性上下文,误导 LLM 执行非预期操作。

**如何预防:**

- 对用户提供的提示实施严格的输入验证和清理。
- 使用上下文感知的过滤和输出编码来防止提示操纵。
- 定期更新和微调 LLM,以提高其对恶意输入和边缘情况的理解。
- 监控和记录 LLM 交互,以检测和分析潜在的提示注入尝试。

**攻击场景示例:**

- 场景 #1:\_ 攻击者制作一个提示,通过让模型认为请求是合法的,从而欺骗 LLM 泄露敏感信息,如用户凭证或内部系统细节。

- 场景 #2:\_ 恶意用户通过使用特定的语言模式、标记或编码机制绕过内容过滤器,而 LLM 未能识别这些内容为受限内容,从而允许用户执行原本应该被阻止的操作。

### 断言实现

我将 `checkForForbiddenWords` 函数包含在 `checkResponseIncludes` 函数中，因为我不想在每个测试中专门调用它。但是，我也希望能够绕过它，因此我添加了一个变量来实现这一点。

Ollama API 提供了一种自动化单一提示和端到端对话的方法。对于端到端对话，我们提供用户和 LLM 的响应，直到最终响应。您可以在 **[GitHub](https://github.com/stuart-thomas-zoopla/LlmTestingWithPlaywright)** 上看到这两种测试类型的示例。

## 改进断言

我决定以两种方式处理断言。第一种是对响应内容进行断言，这对任何做过 API 测试的人来说都很熟悉。

### 对响应内容进行断言

对于这部分测试，我只是断言响应包含某个关键字或短语。我为此创建了一个可重用的助手函数。

```typescript
for (const word of expectedWords) {
  expect(responseString.includes(word)).toBeTruthy();
}
```

该函数设计为可以提供单个字符串或多个字符串（作为数组）。这使我能够创建检查响应中是否包含单词或短语的断言，或者它们的组合。

需要以允许 LLM 响应变化的方式进行断言，这使我们可能会遇到不稳定的测试结果。我们真正需要的是评估答案是否传达了我们预期的信息。

### 使用 LLM 测试 LLM

我们可以使用 LLM 来测试预期响应和实际响应在语义上是否相似，我称这种方法为评估 LLM。这样我们就不需要知道将要收到的确切响应，只需了解 LLM 对提示的回答大致会是什么样。

为此，我们提供一个类似这样的提示。

```
If the following 2 statements appear to give accurate and corroborating answers to the same question respond 'Yes, the statements are similar'.
Statement 1 - {{originalResponse}} - end of statement 1. Statement 2 - {{expectedResponse}} - end of statement2
```

当然，这意味着我们在用另一个黑箱测试一个黑箱。在我的示例中，我们实际上使用相同的 LLM 进行比较。尽管这并不理想，但可以用来演示概念。这确实可能会导致 LLM 的不正确评估，但提供了另一种检查响应的方法。需要指出的是，我创建的这个提示可能远非完美，需要随着时间的推移不断改进，但它可以用于概念演示。

![Image 3](https://www.thequalityduck.co.uk/wp-content/uploads/2024/04/image-12.png)

### 为什么不两者兼用？

我认为目前这种测试的最佳方法是结合传统断言和评估 LLM 的方法。这样，您可以使用传统断言检查响应中是否包含（或不包含）特定关键字，并使用评估 LLM 提供对预期答案语义相似度的信心。

在 **[GitHub](https://github.com/stuart-thomas-zoopla/LlmTestingWithPlaywright)** 上，我提供了一个使用评估 LLM 的示例测试。在这个示例中，我再次使用 Llama 2 评估其提供的答案质量，并将其与已知答案进行对比。

## 专用 LLM 测试工具

市面上有专门的 LLM 测试工具，我在使用 Playwright 之前也看过几个。

### promptize

其中一个我想进一步调查的是 **[promptize](https://github.com/preset-io/promptimize)**，因为它提供了一些使用 Playwright 这样的工具时不存在的额外功能。不幸的是，它专门支持 OpenAI，经过快速研究后，我决定重构它以支持其他工具和模型需要投入更多时间和精力，这超出了我目前的能力范围。也许将来会有机会继续研究。

### promptfoo

我还发现了 **[promptfoo](https://github.com/promptfoo/promptfoo)**，看起来很有前途。它比 promptize 更开放，并且提供了一些不错的原生功能，包括创建测试矩阵。

我尚未投入足够的时间来研究 promptfoo。相对于我的 Playwright 解决方案，使用这样的工具确实更有吸引力，因此我肯定会在未来继续研究。我预计要获得一致的结果，我需要比目前更多地定制我的配置。

### Trulens

**[Trulens](https://www.trulens.org/)** 类似于 promptfoo。它提供了一种评估 LLM 质量的方法，而不是严格的测试工具。在撰写本文时，我仍在研究 Trulens，但它看起来很有前途，我会很快写一篇关于它的完整文章。

## 总结

自动化提示测试感觉就像是 web 应用程序的自动化 UI 测试。它不需要了解底层的运行机制，并且类似于最终用户体验应用程序的方式。然而，由于不同的原因，它也具有一些相同的缺点，主要是运行成本高昂。在 LLM 的情况下，这是因为当它们托管在云上时，您会因每次提示而被收费。

自动化提示测试是我们开始自动化测试的一个很好的起点，但我们绝对需要深入了解底层机制，以最有效地进行测试。在未来的文章中，我希望进一步探索专用的 LLM 测试工具，以及研究专业的可观测性工具，敬请期待！

## 来源

[来源](https://www.thequalityduck.co.uk/testing-ai-how-to-create-automated-prompt-testing-with-playwright/)

发布时间: 2024-04-04
