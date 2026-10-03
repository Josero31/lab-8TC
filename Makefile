CC = gcc
CFLAGS = -O2 -Wall

all: bin/problema1 bin/problema2 bin/problema3

bin/%: src/%.c
	@mkdir -p bin
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -rf bin

.PHONY: all clean
