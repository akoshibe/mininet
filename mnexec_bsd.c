/*
 * The *BSD (at this time) counterparts to the Linux-specific functions called
 * by mnexec. Since they deal with cgroups/manespaces they are largly
 * non-applicable and are ignored. 
 */

#include "mnexec.h"

#include <stdio.h>

int setns(int unused, int unused2)
{
    (void)unused; (void)unused2;
    return 0; 
}

int try_contain()
{
    return 0;
}


int try_schedrt(const char * unused)
{
    (void)unused;
    return 0;
}

void cgroup(char *unused)
{
    (void)unused;
}

void usage(char *name)
{
    printf("Execution utility for Mininet\n\n"
           "Usage: %s [-cdp] cmd args...\n\n"
           "Options:\n"
           "  -c: close all file descriptors except stdin/out/error\n"
           "  -d: detach from tty by calling setsid()\n"
           "  -p: print ^A + pid\n"
           "  -v: print version\n"
           ,
           name);
}
