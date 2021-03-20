## 描述

这是个腾讯云-云API3.0平台的Node.js库。

在官方的库之上做了包装，以更符合js风格的api来进行调用，官方仓库见：

https://github.com/TencentCloud/tencentcloud-sdk-nodejs

## 安装 

`npm install tencentcloud`

## 示例

```js
const tencentcloud = require('tencentcloud')

async function main() {
  let sdk = new tencentcloud({
    // 必填
    secretId: 'YOUR_SECRET_ID',
    secretKey: 'YOUR_SECRET_KEY',
    serviceType: 'cvm',
    
    // 选填
    region: 'ap-guangzhou', // 不填则默认 `ap-guangzhou`
    version: 'v20170312', // 不填则默认使用最新version
  })
  
  // https://cloud.tencent.com/document/api/213/15728
  const response = await sdk.call('DescribeInstances', {
    Filters: [
      {
        Name: "zone",
        Values: ["ap-guangzhou-1", "ap-guangzhou-2"]
      },
    ]
  })
  
  console.log(response)
}
main()
```

初始化sdk完成后，根据腾讯云的文档来决定要调用的action名称和参数，传入`.call`方法中即可。

腾讯云API中心： https://cloud.tencent.com/document/api

## license

MIT