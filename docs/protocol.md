# SPI control protocol

Each MCU is an SPI mode-0 slave on the shared clock/MOSI/MISO bus and has an
independent active-low chip select. The inactive slave configures MISO as an
input (high impedance); it must never drive the shared line while its CS is
high.

Frames are `A5 command length payload crc8`. Length is one byte and covers only
the payload. CRC is CRC-8/ATM (polynomial `0x07`, initial value zero) over every
preceding byte including sync. Multi-byte integers are little-endian.

| Value | Command | Request payload |
|---:|---|---|
| `0x01` | ARM | none |
| `0x02` | DISARM | none |
| `0x03` | EMERGENCY_STOP | none; fault latches |
| `0x10` | SET_THROTTLE | duty, `uint16` |
| `0x11` | SET_PWM_FREQUENCY | hertz, `uint32` |
| `0x12` | SET_CURRENT_LIMIT | milliamps, `uint32` |
| `0x13` | SET_RAMP_RATE | electrical steps/s², `uint32` |
| `0x14` | SET_DIRECTION | `0` forward, `1` reverse |
| `0x20` | READ_TELEMETRY | none |
| `0x21` | READ_FAULTS | none |
| `0x22` | READ_VERSION | none |

Any malformed length, unknown command, or CRC mismatch is discarded without
changing outputs. The valid-control watchdog is refreshed only after a complete,
accepted control frame. It forces a latched coast-safe fault after 100 ms.
