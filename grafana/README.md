### DASHBOARD ALPHA

Requirements: Datatable Panel Plugin _(`grafana-cli plugins install briangann-datatable-panel`)_

* https://grafana.com/grafana/plugins/briangann-datatable-panel/

Exporter repository maintain by Pixiemars:

* https://github.com/pixiemars/CasperPrometheusGrabber

Exporter default port `8123`

* Prometheus example:

```
global:
  scrape_interval:     1s
  evaluation_interval: 1s

  - job_name: 'casper'
    static_configs:
    - targets: ['10.0.0.1:8888']

  - job_name: 'chain'
    static_configs:
    - targets: ['10.0.0.1:8123']
```

![1](https://user-images.githubusercontent.com/50751381/115509785-633d5c00-a26e-11eb-9a41-2a8cfd33124b.jpg)
![2](https://user-images.githubusercontent.com/50751381/115509798-66d0e300-a26e-11eb-8b76-9df1045806d2.jpg)
![3](https://user-images.githubusercontent.com/50751381/115509811-6a646a00-a26e-11eb-8448-27ed5892a073.jpg)
![4](https://user-images.githubusercontent.com/50751381/115509821-6c2e2d80-a26e-11eb-8baa-a9edfcd8ebfb.jpg)
