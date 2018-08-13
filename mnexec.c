/* mnexec: execution utility for mininet
 *
 * Starts up programs and does things that are slow or
 * difficult in Python, including:
 *
 *  - closing all file descriptors except stdin/out/error
 *  - detaching from a controlling tty using setsid
 *  - running in network and mount namespaces
 *  - printing out the pid of a process so we can identify it later
 *  - attaching to a namespace and cgroup
 *  - setting RT scheduling
 *
 * Partially based on public domain setsid(1)
*/

#include <sys/types.h>

#include <fcntl.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "mnexec.h"

int main(int argc, char *argv[])
{
    int c;
    int fd;
    char buf[PATH_MAX];
    char path[PATH_MAX];
    int nsid;
    int pid;
    char *cwd;

    while ((c = getopt(argc, argv, OPTS)) != -1)
        switch(c) {
        case 'c':
            /* close file descriptors except stdin/out/error */
            for (fd = getdtablesize(); fd > 2; fd--)
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
        case 'n':
            if(try_contain() < 0) {
                return 1;
            }
            break;
        case 'a':
            /* Attach to pid's network namespace and mount namespace */
            pid = atoi(optarg);
            snprintf(path, sizeof(path), "/proc/%d/ns/net", pid);
            nsid = open(path, O_RDONLY);
            if (nsid < 0) {
                perror(path);
                return 1;
            }
            if (setns(nsid, 0) != 0) {
                perror("setns");
                return 1;
            }
            /* Plan A: call setns() to attach to mount namespace */
            snprintf(path, sizeof(path), "/proc/%d/ns/mnt", pid);
            nsid = open(path, O_RDONLY);
            if (nsid < 0 || setns(nsid, 0) != 0) {
                /* Plan B: chroot/chdir into pid's root file system */
                snprintf(path, sizeof(path), "/proc/%d/root", pid);
                if (chroot(path) < 0) {
                    perror(path);
                    return 1;
                }
            }
            /* chdir to correct working directory */
            cwd = getcwd(buf, sizeof(buf));
            if (chdir(cwd) != 0) {
                perror(cwd);
                return 1;
            }
            break;
        case 'g':
            /* Attach to cgroup */
            cgroup(optarg);
            break;
        case 'r':
            /* Set RT scheduling priority */
            if (try_schedrt(optarg) < 0) {
                perror("sched_setscheduler");
                return 1;
            }
            break;
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
