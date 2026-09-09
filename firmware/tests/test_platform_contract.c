#include <assert.h>
#include <stdio.h>

char platform_channel_identity(void);

int main(void) {
#ifdef EXPECT_CHANNEL
    assert(platform_channel_identity() == EXPECT_CHANNEL);
#else
#error EXPECT_CHANNEL must be set by the build
#endif
    puts("platform contract passed");
    return 0;
}
