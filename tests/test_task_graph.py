import csv
import os
import unittest

PROC_FILE = "/proc/task_graph"


def read_kernel_processes():
    processes = []

    with open(PROC_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)

        for row in reader:
            if len(row) != 4:
                continue

            try:
                pid = int(row[0])
                ppid = int(row[1])
            except ValueError:
                continue

            processes.append({
                "pid": pid,
                "ppid": ppid,
                "name": row[2],
                "state": row[3]
            })

    return processes


class TestTaskGraph(unittest.TestCase):

    def setUp(self):
        self.processes = read_kernel_processes()

    def test_proc_file_exists(self):
        """Kernel Module-ийн proc файл байгаа эсэх"""
        self.assertTrue(os.path.isfile(PROC_FILE))

    def test_process_list_not_empty(self):
        """Процессын жагсаалт хоосон биш эсэх"""
        self.assertGreater(len(self.processes), 0)

    def test_pid_is_valid(self):
        """PID эерэг бүхэл тоо эсэх"""
        for process in self.processes:
            self.assertGreater(process["pid"], 0)

    def test_ppid_is_valid(self):
        """PPID сөрөг биш эсэх"""
        for process in self.processes:
            self.assertGreaterEqual(process["ppid"], 0)

    def test_process_name_exists(self):
        """Процессын нэр хоосон биш эсэх"""
        for process in self.processes:
            self.assertTrue(process["name"].strip())

    def test_pid_is_unique(self):
        """PID давхардаагүй эсэх"""
        pids = [p["pid"] for p in self.processes]
        self.assertEqual(len(pids), len(set(pids)))

    def test_systemd_exists(self):
        """PID 1 процесс байгаа эсэх"""
        pids = [p["pid"] for p in self.processes]
        self.assertIn(1, pids)

    def test_process_state_exists(self):
        """Процессын төлөв хоосон биш эсэх"""
        for process in self.processes:
            self.assertTrue(process["state"].strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
