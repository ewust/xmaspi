#define __KERNEL__
#define MODULE

#include <linux/module.h>  
#include <linux/slab.h>
#include "../include/asm/uaccess.h"
#include <linux/fs.h>
#include <linux/delay.h>
#include <linux/gpio.h>

static ssize_t xmas_write(struct file *, const char *, size_t, loff_t *);

static int xmas_major;
#define DEVICE_NAME "xmas"
#define XMAS_OUT 17 // TODO: make this a module param

/* Functions for character device */
struct file_operations xmas_fops = {
    .read = NULL,
    .write = xmas_write,
    .open = NULL,
    .release = NULL
};


int init_module()
{
    printk("Loading the XMAS lights LKM...\n");

    /* Initialize the /dev/xmas character device
     * After load, use `mknod /dev/xmas c 252 0` to create
     * device (replace 252 with whatever xmas_major is) */
    xmas_major = register_chrdev(0, DEVICE_NAME, &xmas_fops);
    if (xmas_major < 0) {
        printk(KERN_ALERT "Registering char device failed with %d\n",
               xmas_major);
        return xmas_major;
    }
    printk("Registered char device %d\n", xmas_major);

    /* Initialize GPIO */
    gpio_direction_output(XMAS_OUT, 0);

    return 0;
}


void cleanup_module()
{
    unregister_chrdev(xmas_major, DEVICE_NAME);

    printk("Unloaded xmas\n");
}

static ssize_t
xmas_write(struct file *filp, const char *in_buf, size_t len, loff_t * off)
{
    unsigned char *buf = in_buf;

    unsigned char cur_buf[5];
    int out_len = 0;

    while (len >= 5) {

        copy_from_user(cur_buf, buf, 5);


        /* 6 bits address
         * 8 bits brightness
         * 4 bits blue
         * 4 bits green
         * 4 bits red */
        unsigned int addr       = cur_buf[0] & 0x3f;
        unsigned int brightness = cur_buf[1];
        unsigned int blue       = cur_buf[2] & 0xf;
        unsigned int green      = cur_buf[3] & 0xf;
        unsigned int red        = cur_buf[4] & 0xf;
        
        unsigned int output = addr << 20 | brightness << 12 | 
                              blue << 8 | green << 4 | red;

        local_irq_disable();

        /* High bit for 10us */
        gpio_set_value(XMAS_OUT, 1);
        udelay(10);

        int i;
        for (i=25; i>=0; i--) {
            if (output & (1 << i)) {
                // High
                gpio_set_value(XMAS_OUT, 0);
                udelay(20);
                gpio_set_value(XMAS_OUT, 1);
                udelay(10);
            } else {
                // Low
                gpio_set_value(XMAS_OUT, 0);
                udelay(10);
                gpio_set_value(XMAS_OUT, 1);
                udelay(20);
            }
        }

        /* Set back to idle */
        gpio_set_value(XMAS_OUT, 0);

        local_irq_enable();

        udelay(30);

        buf += 5;
        len -= 5;
        out_len += 5;
    }
    
    /* This might result in some weird (read: broken) behavior
     * if/when data is fragmented across multiple write calls
     * (page boundary?) */
    if (len != 0) {
        return -EINVAL;
    }
    return out_len;
}


MODULE_AUTHOR("Eric Wustrow");
MODULE_DESCRIPTION("Bit-bang GPIO 17 to drive xmas LEDs ");
MODULE_LICENSE("GPL");
