.PHONY: test test-c test-python clean

CC ?= gcc
CFLAGS ?= -std=c11 -Wall -Wextra -Werror -pedantic

test: test-python test-c

test-python:
	.venv/bin/python -m pytest tests -q

build/test_control: firmware/common/control.c firmware/tests/test_control.c firmware/include/edf_esc/control.h
	mkdir -p build
	$(CC) $(CFLAGS) -Ifirmware/include firmware/common/control.c firmware/tests/test_control.c -o $@

build/test_sensorless: firmware/common/sensorless.c firmware/tests/test_sensorless.c firmware/include/edf_esc/sensorless.h
	mkdir -p build
	$(CC) $(CFLAGS) -Ifirmware/include firmware/common/sensorless.c firmware/tests/test_sensorless.c -o $@

build/test_platform_a: firmware/platform/py32f030/platform_contract.c firmware/tests/test_platform_contract.c
	mkdir -p build
	$(CC) $(CFLAGS) -Ifirmware/include -Ifirmware/platform/py32f030 -Ifirmware/esc_a -DEXPECT_CHANNEL=\'A\' $^ -o $@

build/test_platform_b: firmware/platform/py32f030/platform_contract.c firmware/tests/test_platform_contract.c
	mkdir -p build
	$(CC) $(CFLAGS) -Ifirmware/include -Ifirmware/platform/py32f030 -Ifirmware/esc_b -DEXPECT_CHANNEL=\'B\' $^ -o $@

test-c: build/test_control build/test_sensorless build/test_platform_a build/test_platform_b
	./build/test_control
	./build/test_sensorless
	./build/test_platform_a
	./build/test_platform_b

clean:
	rm -f build/test_control
