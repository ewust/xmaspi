obj-m = xmas.o
ccflags-y := -Wno-declaration-after-statement -Wno-unused-result
KVERSION = $(shell uname -r)
all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
