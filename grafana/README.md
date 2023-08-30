#### CASPER NODE DASHBOARD

_**Update:** Current release is approach to adopt breaking changes in v1.5.2_

* _Casper node serves metrics by default on `http://127.0.0.1:8888/metrics`_

* _Grafana version: >= **v10.0.3** ( Please keep your instance up to date )_

* _Grafana alerts system doesn't support variables, examples included, but should be set on specific target manualy !_

#### Prometheus example:

```
global:
  scrape_interval:     15s
  evaluation_interval: 15s

  - job_name: 'casper'
    static_configs:
    - targets: ['127.0.0.1:8888']

```
