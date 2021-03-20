const officialSdk = require("tencentcloud-sdk-nodejs")


class Sdk {
  constructor(options) {
    const self = this;

    if (!options.secretId || !options.secretKey || !options.serviceType) {
      throw Error('must provide `secretId`, `secretKey`, `serviceType`')
    }

    self.secretId = options.secretId;
    self.secretKey = options.secretKey;
    self.serviceType = options.serviceType;
    if (!officialSdk[self.serviceType]) {
      throw Error(`service type '${self.serviceType}' is not exist`)
    }

    // optional args
    self.version = options.version || self.getServiceTypeLatestVersion(self.serviceType);
    if (!officialSdk[self.serviceType][self.version]) {
      throw Error(`version '${self.version}' is not exist`)
    }
    self.region = options.region || 'ap-guangzhou';

    self.client = null;
    self.models = null;


    self.init()
  }

  init() {
    const self = this;

    const Client = officialSdk[self.serviceType][self.version].Client;
    const models = officialSdk[self.serviceType][self.version].Models;
    const Credential = officialSdk.common.Credential;

    const cred = new Credential(self.secretId, self.secretKey);
    const client = new Client(cred, self.region);

    self.client = client;
    self.models = models;
  }

  getServiceTypeLatestVersion(serviceType) {
    const Client = officialSdk[serviceType];
    const keys = Object.keys(Client);

    // 过滤出所有version
    const versions = keys.filter(function (key) {
      return /v\d{8}/.test(key);
    })
    versions.sort();

    // 排序后的最后一个就是最新的version
    const latestVersion = versions[versions.length - 1]

    return latestVersion
  }

  call(actionName, actionParams) {
    const self = this;

    const req = new self.models[`${actionName}Request`]();

    req.deserialize(actionParams);
    return new Promise(function (resolve, reject) {
      self.client[actionName](req, function(err, response) {
        if (err) {
          reject(err);
          return;
        }
        resolve(response);
      });
    })
  }
}

module.exports = Sdk;