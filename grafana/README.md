#### [CASPER NODE](https://github.com/casper-network) DASHBOARD

_**Update:** Current release state is approach to adopt breaking changes in v1.5.6_

* _Casper node serves metrics by default on `curl -s http://127.0.0.1:8888/metrics`_

* _Grafana version: >= **v10.3.1** ( Please keep your instance up to date )_

* _Grafana **alerts system doesn't support variables**, examples included, but should be set on specific target manualy !_

#### Prometheus configuration example:

_By following this example Prometheus configuration, the dashboard should work out of the box. If it doesn't work as expected, please refer to the Troubleshooting section below._

```toml
Make sure your target IP is correct !
```

```
global:
  scrape_interval:     15s
  evaluation_interval: 15s

  - job_name: 'casper_node'
    static_configs:
    - targets: ['127.0.0.1:8888']
      labels:
        alias: 'Casper Archive LA 1'
        instance: my-casper-us-1

```

#### Dashboard integration:

**With provided json from this repository:**

* Download `validator_dashboard.json`
* In **Grafana UI** go to Dashboards
* Click **New** to reveal menue
* Click **Import**
* Choose json file using `Upload dashboard JSON file`

#### Troubleshooting

In the Grafana dashboard configuration, the regular expression (regex) is currently set to match any sources that contain the string `cas`. If you need to modify this behavior, you can change the regex value in the dashboard's variables settings.

To update the regex, follow these steps:

* Go to the dashboard settings by clicking the gear icon on the top right.
* Locate the variables settings.
* Find the regex field for "job / instance".
* Set the new Regex pattern to match your preferred keyword, e.g., `/my_new_keyword/i`.

#### Get help

Support available in ~~Discord and ( RIP )~~ [Telegram Dedicated Chat](https://t.me/CasperTestNet)

[Casper Network GitHub Repository](https://github.com/casper-network)
