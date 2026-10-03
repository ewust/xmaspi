#include "lights.h"

#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <event2/event.h>

// Each datagram is one full frame. Skip ahead to the newest queued
// frame so the lights don't fall behind the sender.
static void read_cb(evutil_socket_t fd, short what, void *arg)
{
    struct lights *lights = arg;
    uint8_t buf[FRAME_STATE_LEN];
    uint8_t latest[FRAME_STATE_LEN];
    int have_frame = 0;
    ssize_t len;

    for (;;) {
        len = recv(fd, buf, sizeof(buf), 0);
        if (len < 0) {
            if (errno == EINTR) {
                continue;
            }
            if (errno != EAGAIN && errno != EWOULDBLOCK) {
                perror("recv");
            }
            break;
        }
        if (len == sizeof(buf)) {
            memcpy(latest, buf, sizeof(latest));
            have_frame = 1;
        }
    }

    if (have_frame) {
        update_lights(lights, latest);
    }
}

int main(int argc, char *argv[])
{
    struct options opts;
    struct lights lights;
    struct event_base *base;
    struct event *ev;
    struct sockaddr_in sin;
    evutil_socket_t sock;

    parse_options(argc, argv, &opts);
    lights_init(&lights);

    base = event_base_new();
    if (base == NULL) {
        fprintf(stderr, "Could not create event base\n");
        exit(EXIT_FAILURE);
    }

    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }
    evutil_make_socket_nonblocking(sock);
    evutil_make_socket_closeonexec(sock);

    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = htonl(INADDR_ANY);
    sin.sin_port = htons(opts.port);

    if (bind(sock, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
        perror("bind");
        exit(EXIT_FAILURE);
    }

    ev = event_new(base, sock, EV_READ|EV_PERSIST, read_cb, &lights);
    if (ev == NULL || event_add(ev, NULL) < 0) {
        fprintf(stderr, "Could not add read event\n");
        exit(EXIT_FAILURE);
    }

    if (opts.verbose) {
        lights_add_status_timer(&lights, base);
    }

    event_base_dispatch(base);

    return 0;
}
