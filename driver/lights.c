#include "lights.h"

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifndef DEV_XMAS
#define DEV_XMAS "/dev/xmas"
#endif
#define FRAME_LEN 5

static void usage(const char *prog)
{
    fprintf(stderr, "usage: %s [-v] [-p port]\n", prog);
    exit(EXIT_FAILURE);
}

void parse_options(int argc, char *argv[], struct options *opts)
{
    int c;
    char *end;
    long port;

    opts->verbose = 0;
    opts->port = DEFAULT_PORT;

    while ((c = getopt(argc, argv, "vp:")) != -1) {
        switch (c) {
        case 'v':
            opts->verbose = 1;
            break;
        case 'p':
            port = strtol(optarg, &end, 10);
            if (*optarg == '\0' || *end != '\0' || port < 1 || port > 65535) {
                usage(argv[0]);
            }
            opts->port = port;
            break;
        default:
            usage(argv[0]);
        }
    }
    if (optind != argc) {
        usage(argv[0]);
    }
}

// Translate a bulb's address (0-100) to a physical address (0-50 and strand)
static void init_led_addrs(struct lights *lights)
{
    int i;
    for (i=0; i<NUM_BULBS; i++) {
        if (i < 50) {
            lights->led_addrs[i] = 49 - i;
        } else {
            lights->led_addrs[i] = (i - 50) | 0x40;
        }
    }
}

void lights_init(struct lights *lights)
{
    memset(lights, 0, sizeof(*lights));
    init_led_addrs(lights);

    // Output goes to stdout, which may be redirected to a file
    setvbuf(stdout, NULL, _IOLBF, 0);

    while (access(DEV_XMAS, F_OK) == -1) {
        sleep(1);
    }

    lights->out_fd = open(DEV_XMAS, O_WRONLY | O_CLOEXEC);
    if (lights->out_fd < 0) {
        perror("open " DEV_XMAS);
        exit(EXIT_FAILURE);
    }
}

static void write_frames(struct lights *lights, const uint8_t *buf, size_t len)
{
    while (len > 0) {
        ssize_t n = write(lights->out_fd, buf, len);
        if (n < 0) {
            if (errno == EINTR) {
                continue;
            }
            perror("write " DEV_XMAS);
            exit(EXIT_FAILURE);
        }
        buf += n;
        len -= n;
    }
}

void update_lights(struct lights *lights, const uint8_t *buf)
{
    // Send all changed bulbs in one write so the kernel driver
    // can update both strands simultaneously
    uint8_t update_buf[NUM_BULBS * FRAME_LEN];
    uint8_t *ptr = update_buf;
    int i;

    for (i=0; i<NUM_BULBS; i++) {
        const uint8_t *b = buf + i * BULB_STATE_LEN;
        uint32_t new_state = (uint32_t)b[0] << 24 | (uint32_t)b[1] << 16 |
                             (uint32_t)b[2] << 8 | b[3];
        if (lights->bulbs[i] != new_state) {
            *ptr++ = lights->led_addrs[i];
            *ptr++ = b[0];      // brightness
            *ptr++ = b[3];      // blue
            *ptr++ = b[2];      // green
            *ptr++ = b[1];      // red
            lights->bulbs[i] = new_state;

            lights->bulb_updates++;
        }
    }

    if (ptr != update_buf) {
        write_frames(lights, update_buf, ptr - update_buf);
    }

    lights->frame_updates++;
}

static void status_cb(evutil_socket_t fd, short what, void *arg)
{
    struct lights *lights = arg;
    printf("%u frames/sec, %u bulbs/sec\n",
           lights->frame_updates, lights->bulb_updates);

    lights->frame_updates = 0;
    lights->bulb_updates = 0;
}

void lights_add_status_timer(struct lights *lights, struct event_base *base)
{
    struct timeval one_sec = {1, 0};
    struct event *ev = event_new(base, -1, EV_PERSIST, status_cb, lights);
    if (ev == NULL || event_add(ev, &one_sec) < 0) {
        fprintf(stderr, "Could not add status timer\n");
        exit(EXIT_FAILURE);
    }
}
