/* mnexec: execution utility for mininet
 *
 * Starts up programs and does things that are slow or
 * difficult in Python, including:
 *
 *  - closing all file descriptors except stdin/out/error
 *  - detaching from a controlling tty using setsid
 *  - printing out the pid of a process so we can identify it later
 *
 * Partially based on public domain setsid(1)
*/

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>

#if !defined(VERSION)
#define VERSION "(devel)"
#endif

void usage(char *name)
{
    printf("Execution utility for Mininet\n\n"
           "Usage: %s [-cdnp] [-a pid] [-g group] [-r rtprio] cmd args...\n\n"
           "Options:\n"
           "  -c: close all file descriptors except stdin/out/error\n"
           "  -d: detach from tty by calling setsid()\n"
           "  -p: print ^A + pid\n"
           "  -v: print version\n",
           name);
}

int main(int argc, char *argv[])
{
    int c;

    while ((c = getopt(argc, argv, "+cdpvh")) != -1)
        switch(c) {
        case 'c':
            /* close file descriptors except stdin/out/error */
            for (int fd = getdtablesize(); fd > 2; fd--)
                close(fd);
            break;
        case 'd':
            /* detach from tty */
            if (getpgrp() == getpid()) {
                switch(fork()) {
                    case -1:
                        perror("fork");
                        return 1;
                    case 0:     /* child */
                        break;
                    default:    /* parent */
                        return 0;
                }
            }
            setsid();
            break;
        case 'p':
            /* print pid */
            printf("\001%d\n", getpid());
            fflush(stdout);
            break;
        case 'v':
            printf("%s\n", VERSION);
            exit(0);
        case 'h':
            usage(argv[0]);
            exit(0);
        default:
            usage(argv[0]);
            exit(1);
        }

    if (optind < argc) {
        execvp(argv[optind], &argv[optind]);
        perror(argv[optind]);
        return 1;
    }

    usage(argv[0]);

    return 0;
}
