# HiSilicon Registers

You can view the generated documentation site at [hisilicon.randomcpu.com](https://hisilicon.randomcpu.com/)

[![Build Website](https://github.com/DeathCamel58/hisilicon-registers/actions/workflows/python-build.yml/badge.svg)](https://github.com/DeathCamel58/hisilicon-registers/actions/workflows/python-build.yml)

## What is this?

HiSilicon's documentation sucks from what I've seen. This is an attempt to create a set of halfway decent RDL files for
their chips, along with a site that reflects the current status of register data in this repository for numerous chips.

## Cross-chip overview

[CROSS-CHIP.md](CROSS-CHIP.md) (generated) shows the SoC family tree, which chip uses which edition of each IP family (UART, GPIO, SPI, I2C, flash controller, Ethernet MAC, USB, SATA, CRG, DMAC, MMC, VICAP, ISP, VDP, RTC, PWM, MIPI RX, VEDU, cipher, USB and SATA PHY drivers) and which Linux or U-Boot driver covers which edition. The diagrams are published with the site under `assets/common/diagrams/`.
