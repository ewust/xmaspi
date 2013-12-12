
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <event2/event.h>
#include <event2/listener.h>
#include <event2/bufferevent.h>
#include <event2/buffer.h>
#include <stdint.h>
#include <string.h>

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
    //char update_buf[NUM_BULBS*5];
    //char *ptr = update_buf;
    char send_buf[5];
    for (i=0; i<NUM_BULBS; i++) {
        uint32_t new_state = ntohl(bulbs_buf[i]);
        if (state->bulbs[i] != new_state) {
            send_buf[0] = state->led_addrs[i];
            send_buf[1] = (new_state >> 24) & 0xff;      // brightness
            send_buf[2] = (new_state >> 0) & 0xff;       // blue
            send_buf[3] = (new_state >> 8) & 0xff;       // green
            send_buf[4] = (new_state >> 16) & 0xff;      // red
            /*
            *ptr++ = state->led_addrs[i];
            *ptr++ = (new_state >> 24) & 0xff;      // brightness
            *ptr++ = (new_state >> 0) & 0xff;       // blue
            *ptr++ = (new_state >> 8) & 0xff;       // green
            *ptr++ = (new_state >> 16) & 0xff;      // red
            */
            state->bulbs[i] = new_state;
            fwrite(send_buf, 5, 1, state->out_f);
            fflush(state->out_f);
            state->bulb_updates++;
        }
    }
    state->frame_updates++;
    /*
    if (ptr != update_buf) {
        ssize_t update_len = (ptr - update_buf);
        fwrite(update_buf, update_len, 1, state->out_f);
        fflush(state->out_f);

        state->bulb_updates += (update_len / 5);
        state->frame_updates++;
    }
    */
}

void read_cb(struct bufferevent *bev, void *arg)
{
    struct state_st *state = arg;
    char buf[NUM_BULBS*4];
    struct sockaddr_in src_addr;
    struct evbuffer *input = bufferevent_get_input(bev);
    int had_input = 0;

    // TODO: use math and evbuffer_drain to save on copying
    while (evbuffer_get_length(input) >= sizeof(buf)) {
        evbuffer_remove(input, buf, sizeof(buf));
        update_lights(state, buf);
        had_input = 1;
    }

    //if (had_input) {
    //    update_lights(state, buf);
    //}
}

void status_cb(evutil_socket_t fd, short what, void *arg)
{
    struct state_st *state = arg;
    printf("%d frames/sec, %d bulbs/sec\n", state->frame_updates, state->bulb_updates);

    state->frame_updates = 0;
    state->bulb_updates = 0;
}

static void
accept_conn_cb(struct evconnlistener *listener,
    evutil_socket_t fd, struct sockaddr *address, int socklen,
    void *arg)
{
        struct state_st *state = arg;
        struct event_base *base = evconnlistener_get_base(listener);
        struct bufferevent *bev = bufferevent_socket_new(
                base, fd, BEV_OPT_CLOSE_ON_FREE);

        bufferevent_setcb(bev, read_cb, NULL, NULL, state);

        bufferevent_enable(bev, EV_READ|EV_WRITE);
}


int main(int argc, char *argv[])
{

    struct event_base *base;
    int sock;
    int port = 1337;
    struct sockaddr_in sin;
    struct state_st state;

    memset(&sin, 0, sizeof(sin));

    base = event_base_new();

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

    struct timeval one_sec = {1, 0};
    ev = event_new(base, 0, EV_PERSIST, status_cb, &state);
    event_add(ev, &one_sec);

    event_base_dispatch(base);

    return 0;
}
