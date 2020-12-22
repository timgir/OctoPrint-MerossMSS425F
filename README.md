# OctoPrint-MerossMSS425F

A simple plugin for shutdown device like printer with Meross MSS425F smart plug

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually using this URL:

    https://github.com/Titome/OctoPrint-MerossMSS425F/archive/master.zip

## Configuration

After that, you need to add email & password at your Meross account & choose plug to shutdown
into your `config.yaml` file at your local Octoprint folder:

```yaml
plugins:
    meross_mss425f:
        email: foo@bar.com
        password: Oct0pr1nt
        multiplug:
            first_plug: true
            usb_plug: true
```

You have `first_plug`, `second_plug`, `third_plug`, `fourth_plug` & `usb_plug`.
