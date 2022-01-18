### CASPER VALIDATOR DASHBOARD

_Update: New performance metric introduced in 1.4.4 implemented, bug fixes and UI adjustments, Grafana min v8.3.3 read below_

* _Due to lack of maintenance on custom exporter some additional metrics been temporaty removed._

* _Casper validator serve metrics by default at `127.0.0.1:8888/metrics`_

* _Grafana version: 8.3.3_ **[ MANDATORY UPGRADE IF CURRENT IS ABOVE 8.x.x CRITICAL SECURITY VULNURABILITY FIX !!! ]**

* _Grafana alerts system doesn't support variables, examples included, but should be set on specific target manualy._

#### Prometheus example:

```
global:
  scrape_interval:     15s
  evaluation_interval: 15s

  - job_name: 'casper'
    static_configs:
    - targets: ['127.0.0.1:8888']

```
![1](https://user-images.githubusercontent.com/50751381/149851735-9133dd55-4ec8-4c9f-8bd8-1d587c7e4ae1.jpg)
![2](https://user-images.githubusercontent.com/50751381/149851752-656da766-f0bb-40c7-9f7b-699ff57bf6d2.jpg)
![3](https://user-images.githubusercontent.com/50751381/149851761-79fd45f0-5eb7-4f15-bab0-2f78bfbdaa93.jpg)
![4](https://user-images.githubusercontent.com/50751381/149851764-be630051-88fd-4c01-9efe-e31081a97446.jpg)
