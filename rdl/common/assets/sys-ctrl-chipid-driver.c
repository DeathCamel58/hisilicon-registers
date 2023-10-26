// SPDX-License-Identifier: GPL-2.0+

#include <common.h>
#include <dm.h>
#include <soc.h>
#include <common.h>
#include <malloc.h>

#include <asm/io.h>

// Ref: https://hisilicon.randomcpu.com/?p=hi3520v100.SYS_CTRL.SCSYSID0
#define SYSID0 0x0
#define SYSID1 0x4
#define SYSID2 0x8
#define SYSID3 0xC

struct soc_hisilicon_plat
{
    const char *family;
    const char *revision;
    bool all_sys_id;
};

/**
 * Returns the family of the chip. This is stored in SYSID1, SYSID2, and SYSID3 registers.
 * @param plat The platform device
 * @param idreg1 The SYSID0 value
 * @param idreg1 The SYSID1 value
 * @param idreg2 The SYSID2 value
 * @param idreg3 The SYSID3 value
 */
static const char *get_family_string(struct soc_hisilicon_plat *plat, u32 idreg0, u32 idreg1, u32 idreg2, u32 idreg3) {
    char *buffer = (char *) malloc(8);

    if (plat->all_sys_id) {
        snprintf(buffer, 8, "Hi%02X%02X%X", idreg3, idreg2, ((idreg1 >> 0x4) & 0xF));
    } else {
        switch (idreg0) {
            case 0x06000001:
                snprintf(buffer, 8, "Hi3516A");
                break;
            case 0x3516A300:
                snprintf(buffer, 8, "Hi3516A");
                break;
            default:
                snprintf(buffer, 8, "Unknown");
                break;
        }
    }

    return buffer;
}

/**
 * Returns the revision of the chip. This is stored in SYSID1 register.
 * @param plat The platform device
 * @param idreg0 The SYSID0 value
 * @param idreg1 The SYSID1 value
 */
static const char *get_rev_string(struct soc_hisilicon_plat *plat, u32 idreg0, u32 idreg1) {
    char *buffer = (char *) malloc(8);

    if (plat->all_sys_id) {
        snprintf(buffer, 8, "V%01X%02X", (idreg1 & 0xF), idreg0);
    } else {
        switch (idreg0) {
            case 0x06000001:
                snprintf(buffer, 8, "V200");
                break;
            case 0x3516A300:
                snprintf(buffer, 8, "V300");
                break;
            default:
                snprintf(buffer, 8, "Unknown");
                break;
        }
    }

    return buffer;
}

static int soc_hisilicon_get_family(struct udevice *dev, char *buf, int size) {
    struct soc_hisilicon_plat *plat = dev_get_plat(dev);

    snprintf(buf, size, "%s", plat->family);

    return 0;
}

static int soc_hisilicon_get_revision(struct udevice *dev, char *buf, int size) {
    struct soc_hisilicon_plat *plat = dev_get_plat(dev);

    snprintf(buf, size, "%s", plat->revision);

    return 0;
}

static const struct soc_ops soc_hisilicon_ops = {
        .get_family = soc_hisilicon_get_family,
        .get_revision = soc_hisilicon_get_revision,
};

int soc_hisilicon_probe(struct udevice *dev) {
    struct soc_hisilicon_plat *plat = dev_get_plat(dev);
    u32 idreg0, idreg1, idreg2, idreg3;
    void *idreg_addr;

    idreg_addr = dev_read_addr_ptr(dev);
    if (!idreg_addr)
        return -EINVAL;

    /* Check if DT specifies that SYSID0-SYSID3 exist */
    plat->all_sys_id = dev_read_bool(dev, "all-sys-id");

    idreg0 = readl(idreg_addr + SYSID0);
    idreg1 = readl(idreg_addr + SYSID1);
    idreg2 = readl(idreg_addr + SYSID2);
    idreg3 = readl(idreg_addr + SYSID3);

    plat->family = get_family_string(plat, idreg0, idreg1, idreg2, idreg3);
    plat->revision = get_rev_string(plat, idreg0, idreg1);

    return 0;
}

static const struct udevice_id soc_hisilicon_ids[] = {
        { .compatible = "hisilicon,hi35xx-chipid" },
        { .compatible = "hisilicon,hi36xx-chipid" }, // TODO: Verify
        {}
};

U_BOOT_DRIVER(soc_hisilicon) = {
        .name           = "soc_hisilicon",
        .id             = UCLASS_SOC,
        .ops        = &soc_hisilicon_ops,
        .of_match       = soc_hisilicon_ids,
        .probe          = soc_hisilicon_probe,
        .plat_auto    = sizeof(struct soc_hisilicon_plat),
};
