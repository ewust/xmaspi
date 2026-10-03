#ifndef LIGHTS_H
#define LIGHTS_H

#include <stdint.h>
#include <event2/event.h>

#define NUM_BULBS 100
#define BULB_STATE_LEN 4
#define FRAME_STATE_LEN (NUM_BULBS * BULB_STATE_LEN)
#define DEFAULT_PORT 1337

struct lights
{
    uint32_t bulbs[NUM_BULBS];  // brightness, red, green, blue as bytes
    uint8_t led_addrs[NUM_BULBS];
    int out_fd;

    // Updates/sec
    uint32_t frame_updates;
    uint32_t bulb_updates;
};

struct options
{
    int verbose;
    uint16_t port;
};

void parse_options(int argc, char *argv[], struct options *opts);

// Waits for /dev/xmas to appear and opens it
void lights_init(struct lights *lights);

// Sends the bulbs that differ from buf, a FRAME_STATE_LEN-byte frame
// of big-endian brightness/red/green/blue words
void update_lights(struct lights *lights, const uint8_t *buf);

// Prints frames/sec and bulbs/sec every second
void lights_add_status_timer(struct lights *lights, struct event_base *base);

#endif
