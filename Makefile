
LDFLAGS+=-levent
CFLAGS+=-O3

udp-driver:	udp-driver.c
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

tcp-driver: tcp-driver.c
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

