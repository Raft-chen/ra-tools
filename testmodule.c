#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <asm/archrandom.h>   /* <-- where arch_get_random_seed_long lives */
#include <asm/cpufeature.h>

static int __init my_init(void)
{
    unsigned long seed;

    pr_info("sizeof(long) = %zu bytes\n", sizeof(long));

    if (boot_cpu_has(X86_FEATURE_RDSEED))
        pr_info("RDSEED supported by CPU\n");
    else
        pr_info("RDSEED NOT supported by CPU\n");    

    if (boot_cpu_has(X86_FEATURE_RDSEED)) {
        if (arch_get_random_seed_longs(&seed, 1)==1) {
            pr_info("RDSEED returned: 0x%lx\n", seed);
        } else {
            pr_info("RDSEED instruction present but no entropy\n");
        }
    } else {
        pr_info("RDSEED not supported by CPU\n");
    }

    return 0;
}

static void __exit my_exit(void)
{
    pr_info("Module unloaded\n");
}

module_init(my_init);
module_exit(my_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Raftchen");
MODULE_DESCRIPTION("Test sizeof(long) and RDSEED in kernel");
