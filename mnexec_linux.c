/* 
 * The Linux-specific features of mnexec. This includes cgroup and namespace
 * handling and scheduler manipulations used by resource-constrained
 * components.
 */

#define _GNU_SOURCE

#include "mnexec.h"

#include <linux/sched.h>
#include <limits.h>
#include <syscall.h>
#include <fcntl.h>
#include <sched.h>
#include <ctype.h>
#include <sys/mount.h>

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

int setns(int fd, int nstype)
{
    return syscall(__NR_setns, fd, nstype);
}

int try_contain()
{
    /* run in network and mount namespaces */
    if (unshare(CLONE_NEWNET|CLONE_NEWNS) == -1) {
        perror("unshare");
        return 1;
    }

    /* Mark our whole hierarchy recursively as private, so that our
     * mounts do not propagate to other processes.
     */

    if (mount("none", "/", NULL, MS_REC|MS_PRIVATE, NULL) == -1) {
        perror("remount");
        return 1;
    }

    /* mount sysfs to pick up the new network namespace */
    if (mount("sysfs", "/sys", "sysfs", MS_MGC_VAL, NULL) == -1) {
        perror("mount");
        return 1;
    }
}


int try_schedrt(const char * optarg) {
    /* Set RT scheduling priority */
    static struct sched_param sp;
    sp.sched_priority = atoi(optarg);
    return sched_setscheduler(getpid(), SCHED_RR, &sp);
}

/* Validate alphanumeric path foo1/bar2/baz */
static void validate(char *path)
{
    char *s;
    for (s=path; *s; s++) {
        if (!isalnum(*s) && *s != '/') {
            fprintf(stderr, "invalid path: %s\n", path);
            exit(1);
        }
    }
}

/* Add our pid to cgroup */
void cgroup(char *gname)
{
    static char path[PATH_MAX];
    static char *groups[] = {
        "cpu", "cpuacct", "cpuset", NULL
    };
    char **gptr;
    pid_t pid = getpid();
    int count = 0;
    validate(gname);
    for (gptr = groups; *gptr; gptr++) {
        FILE *f;
        snprintf(path, PATH_MAX, "/sys/fs/cgroup/%s/%s/tasks",
                 *gptr, gname);
        f = fopen(path, "w");
        if (f) {
            count++;
            fprintf(f, "%d\n", pid);
            fclose(f);
        }
    }
    if (!count) {
        fprintf(stderr, "cgroup: could not add to cgroup %s\n",
            gname);
        exit(1);
    }
}

void usage(char *name)
{
    printf("Execution utility for Mininet\n\n"
           "Usage: %s [-cdnp] [-a pid] [-g group] [-r rtprio] cmd args...\n\n"
           "Options:\n"
           "  -c: close all file descriptors except stdin/out/error\n"
           "  -d: detach from tty by calling setsid()\n"
           "  -p: print ^A + pid\n"
           "  -v: print version\n"
           "  -n: run in new network and mount namespaces\n"
           "  -a pid: attach to pid's network and mount namespaces\n"
           "  -g group: add to cgroup\n"
           "  -r rtprio: run with SCHED_RR (usually requires -g)\n"
           ,
           name);
}
