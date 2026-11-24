# cockpit

Cockpit Angular 18 des gérants (composants standalone, signals, nouveau control flow) : calcul de la VL, performance, contributions par titre et alertes, à partir de fund-api.

```bash
npm ci
npm start            # http://localhost:4200, /api relayé vers fund-api (proxy.conf.json)
npm test -- --watch=false   # 5 tests Karma/Jasmine (ChromeHeadless sans sandbox)
```
