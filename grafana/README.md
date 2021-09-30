### CASPER VALIDATOR DASHBOARD

* _Due to lack of maintenance on custom exporter some additional metrics been temporaty removed._

* _Casper validator serve metrics by default at `127.0.0.1:8888/metrics`_

* _Grafana version: 8.1.2_

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

![1](https://user-images.githubusercontent.com/50751381/135534072-e0779742-e015-40ae-84fb-f61f9c49c145.png)
![2](https://user-images.githubusercontent.com/50751381/135534083-7744f44e-8447-4d59-9237-882ade28b7f4.png)
![3](https://user-images.githubusercontent.com/50751381/135534091-684d9354-be4f-4932-bb76-d5149374674b.png)
![4](https://user-images.githubusercontent.com/50751381/135534097-fdb81875-7e84-4e26-98b9-77b0b51dfe6d.png)
![5](https://user-images.githubusercontent.com/50751381/135534105-d03c968f-cc8a-4a94-83cd-73d67e9852e1.png)
