#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/sched/signal.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>

#define PROC_NAME "task_graph"

static int task_graph_show(struct seq_file *m, void *v)
{
    struct task_struct *task;

    seq_puts(m, "PID,PPID,NAME,STATE\n");

    rcu_read_lock();

    for_each_process(task) {
        pid_t ppid = 0;

        if (rcu_dereference(task->real_parent))
            ppid = task_pid_nr(
                rcu_dereference(task->real_parent)
            );

        seq_printf(
            m,
            "%d,%d,%s,%u\n",
            task_pid_nr(task),
            ppid,
            task->comm,
            READ_ONCE(task->__state)
        );
    }

    rcu_read_unlock();

    return 0;
}

static int task_graph_open(struct inode *inode, struct file *file)
{
    return single_open(file, task_graph_show, NULL);
}

static const struct proc_ops task_graph_ops = {
    .proc_open    = task_graph_open,
    .proc_read    = seq_read,
    .proc_lseek   = seq_lseek,
    .proc_release = single_release,
};
static struct proc_dir_entry *task_graph_entry;
static int __init task_graph_init(void)
{
    task_graph_entry = proc_create(
        PROC_NAME, 0444, NULL, &task_graph_ops
    );

    if (!task_graph_entry)
        return -ENOMEM;

    pr_info("Task Graph module loaded\n");
    return 0;
}

static void __exit task_graph_exit(void)
{
    proc_remove(task_graph_entry);
    pr_info("Task Graph module unloaded\n");
}

module_init(task_graph_init);
module_exit(task_graph_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("OS Project");
MODULE_DESCRIPTION("Linux Kernel Module for Listing Tasks");