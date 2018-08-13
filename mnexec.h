#if !defined(VERSION)
#define VERSION "(devel)"
#endif

#ifdef __linux__
#define OPTS "+cdnpa:g:r:vh"
#else
#define OPTS "+cdpvh"
#endif

int setns(int, int);
int try_contain(void);
int try_schedrt(const char *);

void cgroup(char *);
void usage(char *);
