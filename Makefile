
LDFLAGS+=-levent
CFLAGS+=-O3

udp-driver:	udp-driver.c
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

tcp-driver: tcp-drvier.c
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

