# Linux Kernel Process Task Graph

## 1. Төслийн танилцуулга

Энэхүү төсөл нь Linux үйлдлийн системийн ажиллаж буй
процессуудын мэдээллийг Kernel Module ашиглан уншиж,
тэдгээрийн эцэг–хүүхэд холбоог графикаар дүрслэх зорилготой.

## 2. Ашигласан технологи

- Ubuntu Linux
- C Programming Language
- Linux Kernel Module
- Python 3
- Tkinter
- NetworkX
- Matplotlib
- Python unittest

## 3. Үндсэн боломжууд

- Linux-ийн процессуудын мэдээллийг унших
- PID, PPID, Name, State харуулах
- Процессын жагсаалт гаргах
- Процессын нэр болон PID-аар хайх
- Процессын төлөвөөр шүүх
- Эцэг–хүүхэд холбоог графикаар дүрслэх
- Мэдээллийг автоматаар шинэчлэх
- Графыг PNG зураг болгон хадгалах

## 4. Төслийн бүтэц

linux-task-graph/
├── src/
│   ├── kernel/
│   │   ├── task_list.c
│   │   └── Makefile
│   └── ui/
│       └── task_graph.py
├── tests/
│   └── test_task_graph.py
├── docs/
└── README.md

## 5. Суулгах заавар

### Шаардлагатай багцууд

```bash
sudo apt update
sudo apt install build-essential linux-headers-$(uname -r) python3-venv python3-tk
```

### Kernel Module хөрвүүлэх

```bash
cd src/kernel
make
```

### Kernel Module ачаалах

```bash
sudo insmod task_list.ko
```

Secure Boot идэвхтэй системд модульд итгэмжлэгдсэн
түлхүүрээр гарын үсэг зурах шаардлагатай байж болно.

### Python виртуал орчин

```bash
cd ../ui
python3 -m venv .venv
source .venv/bin/activate
pip install matplotlib networkx
```

## 6. Програм ажиллуулах

```bash
python3 task_graph.py
```

## 7. Тест ажиллуулах

Төслийн үндсэн хавтаснаас:

```bash
python3 tests/test_task_graph.py
```

## 8. Туршилтын үр дүн

Нийт 8 автомат тест ажиллуулсан.

Үр дүн:

```text
Ran 8 tests in 0.004s

OK
```

Бүх тест амжилттай болсон.

## 9. Дүгнэлт

Linux Kernel Module ашиглан бодит процессуудын
мэдээллийг уншиж, Python интерфейсээр график
дүрслэл хийх системийг хэрэгжүүлсэн.

Төсөл нь Linux процессын удирдлага болон
эцэг–хүүхэд процессын хамаарлыг ойлгоход
зориулагдсан.

