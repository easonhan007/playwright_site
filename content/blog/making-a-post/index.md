+++
date = 2022-03-12
title = "使用 Playwright API 的 POST 请求上传 Content-Type 为 multipart/form-data 的文件"
description = ""
authors = ["乙醇"]
[taxonomies]
tags = ["playwright基础", "翻译"]
[extra]
math = false
image = "banner.jpg"
+++

在为我的 API 编写自动化脚本时，我遇到了一个问题：如何使用 Playwright API 发起 POST 请求来上传文件。最后，我在一个 [Slack 对话里](https://playwright.slack.com/archives/CSUHZPVLM/p1638175756183800?thread_ts=1638175752.183700&cid=CSUHZPVLM) 找到了答案，于是决定在这里分享。

我尝试进行的 API 调用是向文件接口发送 POST 请求以上传文件，下面的例子中是一个 .png 文件。接口要求请求类型必须为 `multipart/form-data`。首先，我查看了 [Playwright 文档](https://playwright.dev/docs/api/class-apirequestcontext#api-request-context-post) 中关于 apiRequestContext.post() 的部分，发现可以传递的一个选项是 `multipart`（而不是通常用于发布 JSON 数据的 data）。

---

- `multipart` <[Object](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object)<[string](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Data_structures#String_type), [string](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Data_structures#String_type)|[number](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Data_structures#Number_type)|[boolean](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Data_structures#Boolean_type)|\[ReadStream\]|[Object](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object)\>> 提供一个对象，该对象将使用 `multipart/form-data` 编码作为 HTML 表单发送，并作为请求体。如果指定了此参数，则 `content-type` 头将被设置为 `multipart/form-data`，除非显式提供。文件值可以传递为 [`fs.ReadStream`](https://nodejs.org/api/fs.html#fs_class_fs_readstream) 或包含文件名、mime 类型及其内容的类文件对象。[#](https://playwright.dev/docs/api/class-apirequestcontext#api-request-context-post-option-multipart)
- `name` <[string](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Data_structures#String_type)\> 文件名
- `mimeType` <[string](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Data_structures#String_type)\> 文件类型
- `buffer` <[Buffer](https://nodejs.org/api/buffer.html#buffer_class_buffer)\> 文件内容

---

在查看文档和 Slack 对话后，我意识到还需要进一步了解如何创建一个 `buffer` 并将其传递到 POST 请求中。之后，我成功地构建了一个运行正常的 Playwright 测试，如下例所示。

```typescript
import { expect, request } from "@playwright/test";
import fs from "fs";
import path from "path";


test("POST: Upload a file", async ({ request, baseURL }) => {
  const file = path.resolve("lib/", "logo.png");
  const image = fs.readFileSync(file);

  const response = await request.post(baseURL + "/files", {
    headers: {
      Accept: "*/*",
      ContentType: "multipart/form-data",
    },
    multipart: {
      file: {
        name: file,
        mimeType: "image/png",
        buffer: image,
      },
      title: "Logo of Business",
    },
  });
  const body = JSON.parse(await response.text());

  expect(response.status()).toBe(201);
  expect(body.title).toBe("Logo of Business");
  expect(body.type).toBe("png");
}
```

更多关于 Http POST 方法不同请求类型的详细信息可以在 [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST) 上找到。

## 来源

来源网址: https://playwrightsolutions.com/making-a-post/

发布时间: 2022-03-12T06:12:26.000Z
