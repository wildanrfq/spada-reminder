from datetime import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from pytz import timezone
from classes import SpadaCtx


class Absen:
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
        "olahraga": "09:00 - 10:00",
        "prak_alpro": "10:30 - 10:45",
        "alpro": "12:00 - 15:00",
        "matdis": "09:45 - 12:30",
        "prak_basdat": "13:00 - 13:15",
        "basdat": "15:00 - 17:30",
        "konseptek": "10:00 - 11:45",
        "pkn": "07:30 - 09:10",
        "kalkulus": "15:00 - 16:45",
    }


def waktu(jam):
    jam, menit = map(int, jam.split(":"))
    return time(jam, menit, tzinfo=timezone("Asia/Jakarta"))


def absen(hari, matkul, waktu):
    return f"Absen Hari {hari} Kelas IF-B\n\nMatkul: {matkul}\nWaktu: {waktu}"


def markup(url):
    return InlineKeyboardMarkup([[InlineKeyboardButton("SPADA", url=url)]])


async def send_absen(context: SpadaCtx, hari, matkul, link_key):
    db = context.application.bot_data["db"]
    users = await db.fetch("SELECT id FROM users;")
    users = [u.id for u in users]
    link_url = Absen.links[link_key]

    for user in users:
        await context.bot.send_message(
            user,
            absen(hari, matkul, Absen.waktu[link_key]),
            reply_markup=markup(link_url),
        )


def create_job_function(hari, matkul, link_key):
    async def job_function(context: SpadaCtx):
        await send_absen(context, hari, matkul, link_key)

    return job_function


def schedule_jobs(job_queue):
    schedule = [
        ("Senin", "Olahraga", "olahraga", "09:00", 1),
        ("Senin", "Praktikum Alpro", "prak_alpro", "10:30", 1),
        ("Senin", "Alpro", "alpro", "12:00", 1),
        ("Rabu", "Matdis", "matdis", "10:00", 3),
        ("Rabu", "Praktikum Basdat", "prak_basdat", "13:00", 3),
        ("Rabu", "Basdat", "basdat", "15:00", 3),
        ("Kamis", "Konsep Teknologi", "konseptek", "15:00", 4),
        ("Jumat", "Pendidikan Pancasila", "pkn", "07:30", 5),
        ("Jumat", "Kalkulus", "kalkulus", "15:00", 5),
    ]

    for hari, matkul, link_key, waktu_str, day in schedule:
        job_function = create_job_function(hari, matkul, link_key)
        job_queue.run_daily(job_function, waktu(waktu_str), days=(day,))

    print("Successfully scheduled jobs.")
