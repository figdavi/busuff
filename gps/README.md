# How to build PlatformIO based project

1. Install PlatformIO Core
2. Download development platform with examples
3. Extract ZIP archive
4. Run these commands:

```bash
# Change directory to example
$ cd platform-espressif8266/examples/arduino-wifiscan

# Build project
$ pio run

# Upload firmware
$ pio run --target upload

# Clean build files
$ pio run --target clean
```