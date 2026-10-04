CFLAGS ?= -O2
CFLAGS += -Wall -Wextra -Wno-unused-parameter
LDLIBS += -levent

all: udp-driver tcp-driver

udp-driver: udp-driver.o lights.o
tcp-driver: tcp-driver.o lights.o

udp-driver.o tcp-driver.o lights.o: lights.h

clean:
	rm -f udp-driver tcp-driver *.o

.PHONY: all clean
