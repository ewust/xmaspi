
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <event2/event.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

#define NUM_BULBS 100
#define DEV_XMAS "/dev/xmas"

struct state_st
{
    uint32_t bulbs[NUM_BULBS];  // brightness, red, green, blue as bytes
    uint8_t led_addrs[NUM_BULBS];
    FILE *out_f;

    // Updates/sec
    uint32_t frame_updates;
    uint32_t bulb_updates;
};

// Translate a bulb's address (0-100) to a physical address (0-50 and strand)
void init_led_addrs(struct state_st *state)
{
    int i;
    for (i=0; i<NUM_BULBS; i++) {
        if (i < 50) {
            state->led_addrs[i] = 49 - i;
        } else {
            state->led_addrs[i] = (i - 50) | 0x40;
        }
    }
}

void update_lights(struct state_st *state, char *buf)
{
    int i;
    uint32_t *bulbs_buf = (uint32_t*)buf;
    char update_buf[5];
    for (i=0; i<NUM_BULBS; i++) {
        uint32_t new_state = ntohl(bulbs_buf[i]);
        if (state->bulbs[i] != new_state) {
            update_buf[0] = state->led_addrs[i];
            update_buf[1] = (new_state >> 24) & 0xff;      // brightness
            update_buf[2] = (new_state >> 0) & 0xff;       // blue
            update_buf[3] = (new_state >> 8) & 0xff;       // green
            update_buf[4] = (new_state >> 16) & 0xff;      // red
            state->bulbs[i] = new_state;

            fwrite(update_buf, sizeof(update_buf), 1, state->out_f);
            fflush(state->out_f);

            state->bulb_updates++;
        }
    }

    state->frame_updates++;
}

void read_cb(evutil_socket_t fd, short what, void *arg)
{
    struct state_st *state = arg;
    char buf[NUM_BULBS*4];
    struct sockaddr_in src_addr;
    socklen_t addr_len;
    size_t len;

    do {
        len = recvfrom(fd, buf, sizeof(buf), 0, (struct sockaddr*)&src_addr, &addr_len);
    } while (len == sizeof(buf));

    update_lights(state, buf);
}

void status_cb(evutil_socket_t fd, short what, void *arg)
{
    struct state_st *state = arg;
    printf("%d frames/sec, %d bulbs/sec\n", state->frame_updates, state->bulb_updates);

    state->frame_updates = 0;
    state->bulb_updates = 0;
}

int main(int argc, char *argv[])
{
    int verbose = 0;
    if (argc == 2 && !strcmp(argv[1], "-v")) {
        verbose = 1;
    }

    struct event_base *base;
    int sock;
    int port = 1337;
    struct sockaddr_in sin;
    struct state_st state;

    memset(&sin, 0, sizeof(sin));

    base = event_base_new();

    while (access(DEV_XMAS, F_OK) == -1) {
        sleep(1);
    }

    init_led_addrs(&state);
    state.out_f = fopen(DEV_XMAS, "w");
    if (state.out_f == NULL) {
        perror("fopen");
        exit(-1);
    }

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        exit(-1);
    }

    evutil_make_socket_nonblocking(sock);

    sin.sin_family = AF_INET;
    sin.sin_port = htons(port);

    if (bind(sock, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
        perror("bind");
        exit(-1);
    }

    struct event *ev = event_new(base, sock, EV_READ|EV_PERSIST, read_cb, &state);
    event_add(ev, NULL);

    if (verbose) {
        struct timeval one_sec = {1, 0};
        ev = event_new(base, 0, EV_PERSIST, status_cb, &state);
        event_add(ev, &one_sec);
    }

    event_base_dispatch(base);

    return 0;
}
