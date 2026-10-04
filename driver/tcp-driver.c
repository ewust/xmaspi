#include "lights.h"

#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <event2/buffer.h>
#include <event2/bufferevent.h>
#include <event2/event.h>
#include <event2/listener.h>

// The stream is a sequence of full frames. Apply only the newest
// complete one so the lights don't fall behind the sender.
static void read_cb(struct bufferevent *bev, void *arg)
{
    struct lights *lights = arg;
    struct evbuffer *input = bufferevent_get_input(bev);
    size_t frames = evbuffer_get_length(input) / FRAME_STATE_LEN;
    uint8_t buf[FRAME_STATE_LEN];

    if (frames == 0) {
        return;
    }

    evbuffer_drain(input, (frames - 1) * FRAME_STATE_LEN);
    evbuffer_remove(input, buf, sizeof(buf));
    update_lights(lights, buf);
}

static void event_cb(struct bufferevent *bev, short what, void *arg)
{
    if (what & (BEV_EVENT_EOF | BEV_EVENT_ERROR)) {
        bufferevent_free(bev);
    }
}

static void accept_conn_cb(struct evconnlistener *listener,
                           evutil_socket_t fd, struct sockaddr *address,
                           int socklen, void *arg)
{
    struct lights *lights = arg;
    struct event_base *base = evconnlistener_get_base(listener);
    struct bufferevent *bev = bufferevent_socket_new(
            base, fd, BEV_OPT_CLOSE_ON_FREE);

    if (bev == NULL) {
        fprintf(stderr, "Could not create bufferevent\n");
        evutil_closesocket(fd);
        return;
    }

    bufferevent_setcb(bev, read_cb, NULL, event_cb, lights);
    bufferevent_enable(bev, EV_READ);
}

int main(int argc, char *argv[])
{
    struct options opts;
    struct lights lights;
    struct event_base *base;
    struct evconnlistener *listener;
    struct sockaddr_in sin;

    parse_options(argc, argv, &opts);
    lights_init(&lights);

    base = event_base_new();
    if (base == NULL) {
        fprintf(stderr, "Could not create event base\n");
        exit(EXIT_FAILURE);
    }

    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = htonl(INADDR_ANY);
    sin.sin_port = htons(opts.port);

    listener = evconnlistener_new_bind(base, accept_conn_cb, &lights,
            LEV_OPT_CLOSE_ON_FREE|LEV_OPT_CLOSE_ON_EXEC|LEV_OPT_REUSEABLE, -1,
            (struct sockaddr*)&sin, sizeof(sin));
    if (listener == NULL) {
        perror("evconnlistener_new_bind");
        exit(EXIT_FAILURE);
    }

    if (opts.verbose) {
        lights_add_status_timer(&lights, base);
    }

    event_base_dispatch(base);

    return 0;
}
