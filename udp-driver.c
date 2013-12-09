
#include <stdio.h>
#include <sys/socket.h>
#include <event/event2.h>
#include <stdint.h>

#define NUM_BULBS 100

struct state_st
{
    uint32_t bulbs[NUM_BULBS];  // brightness, red, green, blue as bytes
    uint8_t led_addrs[NUM_BULBS];
    FILE *out_f;
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
    char update_buf[NUM_BULBS*5];
    char *ptr = update_buf;
    for (i=0; i<NUM_BULBS; i++) {
        uint32_t new_state = bulbs_buf[i];
        if (state->bulbs[i] != new_state) {
            *ptr++ = state->led_addrs[i];
            *ptr++ = (new_state >> 24) & 0xff;      // brightness
            *ptr++ = (new_state >> 0) & 0xff;       // blue
            *ptr++ = (new_state >> 8) & 0xff;       // green
            *ptr++ = (new_state >> 16) & 0xff;      // red
        }
    }

    if (ptr != update_buf) {
        ssize_t update_len = (ptr - update_buf);
        fwrite(update_buf, update_len, 1, state->out_f);
        fflush(state->out_f);
    }
}

void cb_func(evutil_socket_t fd, short what, void *arg)
{
    struct state_st *state = arg;
    char buf[NUM_BULBS*4];
    struct sockaddr_in src_addr;
    socklen_t addr_len;
    ssize_t len;

    do {
        len = recvfrom(fd, buf, sizeof(buf), 0, &src_addr, &addr_len);
    } while (len == sizeof(buf));

    update_lights(state, buf);
}

int main(int argc, char *argv[])
{

    struct event_base *base;
    int sock;
    int port = 1337;
    struct sockaddr_in sin;
    struct state_st state;


    base = event_init();

    init_led_addrs(&state);
    state.out_f = fopen("/dev/xmas", "r");


    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        exit(-1);
    }

    evutil_make_socket_nonblocking(sock);

    sin.sin_family = AF_INET;
    sin.sin_port = htons(port);

    if (bind(sock, (sturct sockaddr *)&sin, sizeof(sin)) < 0) {
        perror("bind");
        exit(-1);
    }

    event_new(base, sock, EV_READ, read_cb, &state);

    event_base_dispatch(base);


    return 0;
}
