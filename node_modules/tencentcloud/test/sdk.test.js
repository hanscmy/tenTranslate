const assert = require('assert')
const tencentcloud = require('../')


let sdk;

describe('test/sdk.test.js', function () {
  before(function () {
    sdk = new tencentcloud({
      secretId: process.env['CNPM_COS_SECRET_ID'],
      secretKey: process.env['CNPM_COS_SECRET_KEY'],
      serviceType: 'cvm',
    })
  })

  describe('init', function () {
    it('should support init with `region`', async function () {
      let mySdk = new tencentcloud({
        secretId: process.env['CNPM_COS_SECRET_ID'],
        secretKey: process.env['CNPM_COS_SECRET_KEY'],
        serviceType: 'cvm',
        region: 'ap-shanghai'
      })

      const response = await mySdk.call('DescribeZones')

      assert(typeof response.TotalCount == 'number')
      assert(/ap\-shanghai\-/.test(response.ZoneSet[0].Zone))
    })

    it('should throw when provide wrong service type', async function () {
      assert.throws(function () {
        let mySdk = new tencentcloud({
          secretId: process.env['CNPM_COS_SECRET_ID'],
          secretKey: process.env['CNPM_COS_SECRET_KEY'],
          serviceType: 'cvmmmmmmmmm',
          region: 'ap-shanghai',
        })
      }, /service type 'cvmmmmmmmmm' is not exist/)
    })

    it('should throw when provide wrong version', async function () {
      assert.throws(function () {
        let mySdk = new tencentcloud({
          secretId: process.env['CNPM_COS_SECRET_ID'],
          secretKey: process.env['CNPM_COS_SECRET_KEY'],
          serviceType: 'cvm',
          region: 'ap-shanghai',
          version: 'v20000000'
        })
      }, /version 'v20000000' is not exist/)
    })
  })

  describe('normal call', function () {
    it('should DescribeZones', async function() {
      const response = await sdk.call('DescribeZones')
      assert(typeof response.TotalCount == 'number')
      assert(/ap\-guangzhou\-/.test(response.ZoneSet[0].Zone))
    })

    it('should DescribeInstances', async function() {
      const response = await sdk.call('DescribeInstances', {
        Filters: [
          {
            Name: "zone",
            Values: ["ap-guangzhou-1", "ap-guangzhou-2"]
          },
        ]
      })
      assert(response.TotalCount > 0)
    })

    it('should DescribeInstances with wrong region', async function() {
      try {
        const response = await sdk.call('DescribeInstances', {
          Filters: [
            {
              Name: "zone",
              Values: ["ap-shanghai-1", "ap-shanghai-2"]
            },
          ]
        })
      } catch (e) {
        assert(e.code == 'InvalidZone.MismatchRegion')
      }
    })
  })

})