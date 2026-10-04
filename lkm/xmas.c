// SPDX-License-Identifier: GPL-2.0
/*
 * Bit-bang GE Color Effects G-35 LED strands from Raspberry Pi GPIOs.
 *
 * Each frame written to /dev/xmas is 5 bytes:
 *   [0] bit 6: strand, bits 0-5: bulb address (63 = broadcast)
 *   [1] brightness
 *   [2] blue  (low 4 bits)
 *   [3] green (low 4 bits)
 *   [4] red   (low 4 bits)
 *
 * Frames for different strands within the same write are sent
 * simultaneously; frames for the same strand go out in order.
 *
 * Bulbs take their address from the first frame they receive after
 * power-up, so loading the module numbers each strand 0 to
 * STRAND_LEN - 1 starting from the end nearest the Pi, and turns
 * all bulbs off.
 */

#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/delay.h>
#include <linux/fs.h>
#include <linux/gpio.h>
#include <linux/miscdevice.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/sched.h>
#include <linux/uaccess.h>

#define NUM_STRANDS	2
#define STRAND_LEN	50
#define FRAME_LEN	5
#define FRAME_BITS	26
#define STRAND_BIT	0x40
#define CHUNK_FRAMES	128

static uint strand0_gpio = 17;
module_param(strand0_gpio, uint, 0444);
MODULE_PARM_DESC(strand0_gpio, "GPIO driving strand 0 (default 17)");

static uint strand1_gpio = 18;
module_param(strand1_gpio, uint, 0444);
MODULE_PARM_DESC(strand1_gpio, "GPIO driving strand 1 (default 18)");

static struct gpio xmas_gpios[NUM_STRANDS];

static DEFINE_MUTEX(xmas_lock);
static u8 xmas_buf[CHUNK_FRAMES * FRAME_LEN]; /* guarded by xmas_lock */

/* Set the data line of every strand in mask to value */
static void set_strands(unsigned int mask, int value)
{
	int s;

	for (s = 0; s < NUM_STRANDS; s++)
		if (mask & BIT(s))
			gpio_set_value(xmas_gpios[s].gpio, value);
}

/*
 * 26-bit frame, sent MSB first: 6 bits address, 8 bits brightness,
 * 4 bits each blue, green, red.
 */
static u32 frame_bits(const u8 *frame)
{
	return (u32)(frame[0] & 0x3f) << 20 | (u32)frame[1] << 12 |
	       (frame[2] & 0xf) << 8 | (frame[3] & 0xf) << 4 |
	       (frame[4] & 0xf);
}

/*
 * Send frames[s] on every strand s in active, simultaneously.
 *
 * The bus idles low. A frame is a 10us high start bit followed by
 * 26 bits of 30us each: a 0 bit is low 10us then high 20us, a 1 bit
 * low 20us then high 10us. Every bit starts with a falling edge and
 * only the rising edge moves, so all strands stay in lockstep.
 * Frames must be at least 30us apart.
 */
static void send_frames(unsigned int active, const u32 *frames)
{
	unsigned long flags;
	unsigned int ones;
	int i, s;

	local_irq_save(flags);

	set_strands(active, 1);
	udelay(10);

	for (i = FRAME_BITS - 1; i >= 0; i--) {
		ones = 0;
		for (s = 0; s < NUM_STRANDS; s++)
			if (frames[s] & BIT(i))
				ones |= BIT(s);
		ones &= active;

		set_strands(active, 0);
		udelay(10);
		set_strands(active & ~ones, 1);
		udelay(10);
		set_strands(ones, 1);
		udelay(10);
	}

	set_strands(active, 0);

	local_irq_restore(flags);

	udelay(30);
}

/*
 * Send nframes frames from buf, pairing each strand's next frame with
 * the other strands' next frames.
 */
static void send_chunk(const u8 *buf, size_t nframes)
{
	size_t next[NUM_STRANDS] = { 0 };
	u32 frames[NUM_STRANDS];
	unsigned int active;
	int s;

	for (;;) {
		active = 0;
		for (s = 0; s < NUM_STRANDS; s++) {
			frames[s] = 0;
			while (next[s] < nframes &&
			       !!(buf[next[s] * FRAME_LEN] & STRAND_BIT) != s)
				next[s]++;
			if (next[s] < nframes) {
				frames[s] = frame_bits(buf + next[s] * FRAME_LEN);
				active |= BIT(s);
				next[s]++;
			}
		}
		if (!active)
			break;

		send_frames(active, frames);
		cond_resched();
	}
}

/*
 * Consumes up to CHUNK_FRAMES whole frames per call and returns the
 * number of bytes consumed, so a frame must not be split across
 * writes. Only frames within the same write are sent in parallel.
 */
static ssize_t xmas_write(struct file *filp, const char __user *ubuf,
			  size_t len, loff_t *off)
{
	size_t nframes = min_t(size_t, len / FRAME_LEN, CHUNK_FRAMES);
	ssize_t ret;

	if (nframes == 0)
		return -EINVAL;

	if (mutex_lock_interruptible(&xmas_lock))
		return -ERESTARTSYS;

	if (copy_from_user(xmas_buf, ubuf, nframes * FRAME_LEN)) {
		ret = -EFAULT;
	} else {
		send_chunk(xmas_buf, nframes);
		ret = nframes * FRAME_LEN;
	}

	mutex_unlock(&xmas_lock);

	return ret;
}

static const struct file_operations xmas_fops = {
	.owner = THIS_MODULE,
	.write = xmas_write,
	.llseek = no_llseek,
};

static struct miscdevice xmas_misc = {
	.minor = MISC_DYNAMIC_MINOR,
	.name = "xmas",
	.fops = &xmas_fops,
	.mode = 0222,
};

/*
 * Give each strand's bulbs addresses 0 to STRAND_LEN - 1 in order,
 * leaving them off. Bulbs that already have an address just turn off.
 */
static void xmas_init_bulbs(void)
{
	u32 frames[NUM_STRANDS];
	int addr, s;

	for (addr = 0; addr < STRAND_LEN; addr++) {
		for (s = 0; s < NUM_STRANDS; s++)
			frames[s] = (u32)addr << 20;
		send_frames(BIT(NUM_STRANDS) - 1, frames);
		cond_resched();
	}
}

static int __init xmas_init(void)
{
	int ret;

	xmas_gpios[0] = (struct gpio){ strand0_gpio, GPIOF_OUT_INIT_LOW, "xmas0" };
	xmas_gpios[1] = (struct gpio){ strand1_gpio, GPIOF_OUT_INIT_LOW, "xmas1" };

	ret = gpio_request_array(xmas_gpios, NUM_STRANDS);
	if (ret) {
		pr_err("requesting GPIOs %u and %u failed: %d\n",
		       strand0_gpio, strand1_gpio, ret);
		return ret;
	}

	xmas_init_bulbs();

	ret = misc_register(&xmas_misc);
	if (ret) {
		pr_err("registering /dev/xmas failed: %d\n", ret);
		gpio_free_array(xmas_gpios, NUM_STRANDS);
		return ret;
	}

	pr_info("driving strands on GPIO %u and %u\n",
		strand0_gpio, strand1_gpio);

	return 0;
}

static void __exit xmas_exit(void)
{
	misc_deregister(&xmas_misc);
	gpio_free_array(xmas_gpios, NUM_STRANDS);
}

module_init(xmas_init);
module_exit(xmas_exit);

MODULE_AUTHOR("Eric Wustrow");
MODULE_DESCRIPTION("Bit-bang GPIOs to drive GE G-35 xmas LEDs");
MODULE_LICENSE("GPL");
