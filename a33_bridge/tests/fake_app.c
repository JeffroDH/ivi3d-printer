/* Stand-in for IVI-Main-Controller in the supervisor test: logs each start, opens the port path once
   (like initOpenPort), sends M2051, then idles. Exits on SIGTERM like a normal process. */
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
int main(void) {
    const char *log = getenv("FAKEAPP_LOG"), *port = getenv("FAKEAPP_PORT");
    char cwd[256] = ""; if (!getcwd(cwd, sizeof cwd)) cwd[0] = 0;
    FILE *f = log ? fopen(log, "a") : NULL;
    int fd = port ? open(port, O_RDWR | O_NOCTTY) : -1;
    char tgt[256] = ""; if (port) { ssize_t k = readlink(port, tgt, sizeof tgt - 1); if (k > 0) tgt[k] = 0; }
    if (f) { fprintf(f, "start pid=%d marker=%s cwd=%s port_open=%d via=%s qt=%s\n", getpid(), getenv("FAKEAPP_MARKER") ? getenv("FAKEAPP_MARKER") : "-", cwd, fd >= 0, tgt[0] ? tgt : "node", getenv("QT_QPA_PLATFORM") ? getenv("QT_QPA_PLATFORM") : "-"); fclose(f); }
    if (fd >= 0 && tgt[0]) { if (write(fd, "M2051\n", 6) < 0) {} }   /* only through the pty; the stub node is a plain file */
    for (;;) pause();
}
