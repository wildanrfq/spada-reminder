from datetime import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from pytz import timezone
from classes import SpadaCtx


class Absen:
    schedule = [
        ("Senin", "Olahraga", "olahraga", "09:00", 1),
        ("Senin", "Praktikum Alpro", "prak_alpro", "10:30", 1),
        ("Senin", "Alpro", "alpro", "12:00", 1),
        ("Rabu", "Matdis", "matdis", "09:45", 3),
        ("Rabu", "Praktikum Basdat", "prak_basdat", "13:00", 3),
        ("Rabu", "Basdat", "basdat", "15:00", 3),
        ("Kamis", "Konsep Teknologi", "konseptek", "10:00", 6),
        ("Kamis", "Pendidikan Agama Islam", "agama", "13:00", 4),
        ("Jumat", "Pendidikan Pancasila", "pkn", "07:30", 5),
        ("Jumat", "Kalkulus", "kalkulus", "15:00", 5),
    ]
    links = {
        "olahraga": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=589583",
        "prak_alpro": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=601299",
        "alpro": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=586689",
        "matdis": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=593185",
        "prak_basdat": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=601316",
        "basdat": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=593819",
        "konseptek": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=594648",
        "pkn": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=595789",
        "kalkulus": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=596280",
    }
    waktu = {
        "olahraga": "09:00 \- 10:00",
        "prak_alpro": "10:30 \- 10:45",
        "alpro": "12:00 \- 15:00",
        "matdis": "09:45 \- 12:30",
        "prak_basdat": "13:00 \- 13:15",
        "basdat": "15:00 \- 17:30",
        "konseptek": "10:00 \- 11:45",
        "agama": "Tidak ada absen SPADA",
        "pkn": "07:30 \- 09:10",
        "kalkulus": "15:00 \- 16:45",
    }

    @classmethod
    def get_matkul_info(cls, current_key):
        for i, item in enumerate(cls.schedule):
            if item[2] == current_key:
                current_title = item[1]
                current_time = cls.waktu.get(current_key, "Time not available")

                if i + 1 < len(cls.schedule):
                    next_key = cls.schedule[i + 1][2]
                    next_title = cls.schedule[i + 1][1]
                    next_time = cls.waktu.get(next_key, "Time not available")
                    return current_title, current_time, next_title, next_time
                else:
                    return current_title, current_time, "No next matkul", "N/A"

        return "Matkul not found", "N/A", "N/A", "N/A"


def waktu(jam):
    jam, menit = map(int, jam.split(":"))
    return time(jam, menit, tzinfo=timezone("Asia/Jakarta"))


def absen(hari, link_key):
    matkul, waktu, next_matkul, next_waktu = Absen.get_matkul_info(link_key)
    splitter = " \- "
    return (
        f"*Absen Hari {hari} Kelas IF\-B*\n\n"
        f"Matkul: *{matkul}*\n"
        f"Jam: *{waktu}*\n\n"
        f"Mata kuliah selanjutnya: *{next_matkul}*\n"
        f"{'Jam: ' if next_matkul != 'Pendidikan Agama Islam' else ''}*{next_waktu.split(splitter)[0] if next_matkul != 'Pendidikan Agama Islam' else next_waktu}*"
    )


def markup(url):
    return InlineKeyboardMarkup([[InlineKeyboardButton("SPADA", url=url)]])


async def send_absen(context: SpadaCtx, hari, link_key):
    link_url = Absen.links[link_key]
    print(absen(hari, link_key))
    await context.bot.send_message(
        -1002309269021,
        absen(hari, link_key),
        parse_mode="MarkdownV2",
        reply_markup=markup(link_url),
    )


def create_job_function(hari, link_key):
    async def job_function(context: SpadaCtx):
        await send_absen(context, hari, link_key)

    return job_function


def schedule_jobs(job_queue):
    for hari, _, link_key, waktu_str, day in Absen.schedule:
        if link_key == "agama":
            continue
        job_function = create_job_function(hari, link_key)
        job_queue.run_daily(job_function, waktu(waktu_str), days=(day,))
