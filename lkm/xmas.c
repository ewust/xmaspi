#include <linux/init.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/mutex.h>
#include <linux/sched.h>
#include <linux/uaccess.h>
#include <linux/delay.h>
#include <linux/gpio.h>

#define DEVICE_NAME "xmas"
#define XMAS_OUT_0 17 // TODO: make these module params
#define XMAS_OUT_1 18

/* Each frame written to /dev/xmas is 5 bytes:
 *   [0] bit 6: strand, bits 0-5: bulb address
 *   [1] brightness
 *   [2] blue  (low 4 bits)
 *   [3] green (low 4 bits)
 *   [4] red   (low 4 bits)
 */
#define FRAME_LEN 5
#define STRAND_BIT 0x40
#define CHUNK_FRAMES 128

static ssize_t xmas_write(struct file *, const char __user *, size_t, loff_t *);

static int xmas_major;
static DEFINE_MUTEX(xmas_lock);
static unsigned char xmas_buf[CHUNK_FRAMES * FRAME_LEN]; /* guarded by xmas_lock */

/* Functions for character device */
static const struct file_operations xmas_fops = {
    .owner = THIS_MODULE,
    .write = xmas_write,
};


static int __init xmas_init(void)
{
    int status;

    printk("Loading the XMAS lights LKM...\n");

    /* Initialize GPIO, idling low */
    status = gpio_request(XMAS_OUT_0, "xmas");
    if (status) {
        printk(KERN_ALERT "gpio_request for GPIO %d failed with %d\n",
                XMAS_OUT_0, status);
        return status;
    }

    status = gpio_request(XMAS_OUT_1, "xmas");
    if (status) {
        printk(KERN_ALERT "gpio_request for GPIO %d failed with %d\n",
                XMAS_OUT_1, status);
        goto free_out_0;
    }

    status = gpio_direction_output(XMAS_OUT_0, 0);
    if (!status)
        status = gpio_direction_output(XMAS_OUT_1, 0);
    if (status) {
        printk(KERN_ALERT "gpio_direction_output failed with %d\n", status);
        goto free_out_1;
    }

    /* Initialize the /dev/xmas character device
     * After load, use `mknod /dev/xmas c 252 0` to create
     * device (replace 252 with whatever xmas_major is) */
    xmas_major = register_chrdev(0, DEVICE_NAME, &xmas_fops);
    if (xmas_major < 0) {
        printk(KERN_ALERT "Registering char device failed with %d\n",
               xmas_major);
        status = xmas_major;
        goto free_out_1;
    }
    printk("Registered char device %d\n", xmas_major);

    return 0;

free_out_1:
    gpio_free(XMAS_OUT_1);
free_out_0:
    gpio_free(XMAS_OUT_0);
    return status;
}


static void __exit xmas_exit(void)
{
    unregister_chrdev(xmas_major, DEVICE_NAME);

    gpio_free(XMAS_OUT_0);
    gpio_free(XMAS_OUT_1);

    printk("Unloaded xmas\n");
}

/* Set the data line of every strand in mask (bit 0: strand 0,
 * bit 1: strand 1) to value */
static void set_strands(unsigned int mask, int value)
{
    if (mask & 1)
        gpio_set_value(XMAS_OUT_0, value);
    if (mask & 2)
        gpio_set_value(XMAS_OUT_1, value);
}

/* 26-bit frame, sent MSB first:
 * 6 bits address
 * 8 bits brightness
 * 4 bits blue
 * 4 bits green
 * 4 bits red */
static u32 frame_bits(const unsigned char *frame)
{
    return (u32)(frame[0] & 0x3f) << 20 | (u32)frame[1] << 12 |
           (frame[2] & 0xf) << 8 | (frame[3] & 0xf) << 4 | (frame[4] & 0xf);
}

/* Send frames[s] on every strand s in active, simultaneously.
 *
 * Every bit takes 30us and starts with a falling edge; only the
 * rising edge moves (10us in for a 0 bit, 20us in for a 1 bit),
 * so frames on both strands stay in lockstep. */
static void send_frames(unsigned int active, const u32 *frames)
{
    unsigned long flags;
    unsigned int ones;
    int i;

    local_irq_save(flags);

    /* Start bit: high for 10us */
    set_strands(active, 1);
    udelay(10);

    for (i = 25; i >= 0; i--) {
        ones = ((frames[0] >> i) & 1) | ((frames[1] >> i) & 1) << 1;
        ones &= active;

        set_strands(active, 0);
        udelay(10);
        set_strands(active & ~ones, 1); /* 0 bits: low 10us, high 20us */
        udelay(10);
        set_strands(ones, 1);           /* 1 bits: low 20us, high 10us */
        udelay(10);
    }

    /* Set back to idle */
    set_strands(active, 0);

    local_irq_restore(flags);

    udelay(30);
}

/* Send nframes frames from buf, pairing each strand's next frame
 * with the other strand's next frame. Frames for the same strand
 * go out in the order written. */
static void send_chunk(const unsigned char *buf, size_t nframes)
{
    size_t next[2] = {0, 0};
    unsigned int active;
    u32 frames[2];
    int s;

    for (;;) {
        active = 0;
        for (s = 0; s < 2; s++) {
            frames[s] = 0;
            while (next[s] < nframes &&
                   !!(buf[next[s] * FRAME_LEN] & STRAND_BIT) != s)
                next[s]++;
            if (next[s] < nframes) {
                frames[s] = frame_bits(buf + next[s] * FRAME_LEN);
                active |= 1 << s;
                next[s]++;
            }
        }
        if (!active)
            break;

        send_frames(active, frames);
        cond_resched();
    }
}

/* Consumes up to CHUNK_FRAMES whole frames per call and returns the
 * number of bytes consumed, so a frame must not be split across
 * writes. Only frames within the same write are sent in parallel. */
static ssize_t
xmas_write(struct file *filp, const char __user *in_buf, size_t len, loff_t *off)
{
    size_t nframes = min_t(size_t, len / FRAME_LEN, CHUNK_FRAMES);

    if (nframes == 0)
        return -EINVAL;

    if (mutex_lock_interruptible(&xmas_lock))
        return -ERESTARTSYS;

    if (copy_from_user(xmas_buf, in_buf, nframes * FRAME_LEN)) {
        mutex_unlock(&xmas_lock);
        return -EFAULT;
    }

    send_chunk(xmas_buf, nframes);

    mutex_unlock(&xmas_lock);

    return nframes * FRAME_LEN;
}

module_init(xmas_init);
module_exit(xmas_exit);

MODULE_AUTHOR("Eric Wustrow");
MODULE_DESCRIPTION("Bit-bang GPIO 17 and 18 to drive xmas LEDs ");
MODULE_LICENSE("GPL");
