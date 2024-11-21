import logging
from datetime import datetime, time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from pytz import timezone
from classes import SpadaCtx, MD

logging.basicConfig()
logging.getLogger("apscheduler").setLevel(logging.DEBUG)


class Absen:
    schedule = [
        ("Senin", "Olahraga", "olahraga", "09:00", 1),
        ("Senin", "Praktikum Alpro", "prak_alpro", "10:30", 1),
        ("Senin", "Alpro", "alpro", "12:00", 1),
        ("Senin", "Logika Informatika", "logika", "15:00", 1),
        ("Rabu", "Matdis", "matdis", "09:45", 3),
        ("Rabu", "Praktikum Basdat", "prak_basdat", "13:00", 3),
        ("Rabu", "Basdat", "basdat", "15:00", 3),
        ("Kamis", "Konsep Teknologi", "konseptek", "10:00", 4),
        ("Kamis", "Pendidikan Agama Islam", "agama", "13:00", 4),
        ("Jumat", "Pendidikan Pancasila", "pkn", "07:30", 5),
        ("Jumat", "Kalkulus", "kalkulus", "15:00", 5),
    ]
    links = {
        "olahraga": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=589583",
        "prak_alpro_c": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=601299",
        "prak_alpro_d": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=601976",
        "alpro": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=586689",
        "logika": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=589502",
        "matdis": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=593185",
        "prak_basdat_b": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=601316",
        "prak_basdat_c": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=601393",
        "basdat": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=593819",
        "konseptek": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=594648",
        "pkn": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=595789",
        "kalkulus": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=596280",
    }
    waktu = {
        "olahraga": "09:00 \- 10:00",
        "prak_alpro": "10:30 \- 10:45",
        "alpro": "12:00 \- 15:00",
        "logika": "15:00 \- 16:45",
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
                current_time = cls.waktu[current_key]
                try:
                    next_key = cls.schedule[i + 1][2]
                    next_title = cls.schedule[i + 1][1]
                except:
                    next_key = "olahraga"
                    next_title = "Olahraga"
                next_time = cls.waktu[next_key]
                curtime = datetime.strptime(current_time.split(" \- ")[0], "%H:%M")
                if "Tidak" not in next_time:
                    nexttime = datetime.strptime(next_time.split(" \- ")[0], "%H:%M")
                    next_time = next_time.split(" \- ")[0]
                    if curtime > nexttime:
                        next_time = f"{next_time} \(Besok\)"
                return current_title, current_time, next_title, next_time


def waktu(jam):
    jam, menit = map(int, jam.split(":"))
    return time(jam, menit, tzinfo=timezone("Asia/Jakarta"))


def absen(hari, link_key):
    matkul, waktu, next_matkul, next_waktu = Absen.get_matkul_info(link_key)
    return (
        f"*Absen Hari {hari} Kelas IF\-B*\n\n"
        f"Matkul: *{matkul}*\n"
        f"Jam: *{waktu}*\n\n"
        f"Mata kuliah selanjutnya: *{next_matkul}*\n"
        f"{'Jam: ' if next_matkul != 'Pendidikan Agama Islam' else ''}*{next_waktu}*\n\n"
        f"*__Perhatikan waktu absennya\! Jangan menunda\-nunda\.__*"
    )


def markup(url, link_key=None):
    if link_key == "prak_alpro":
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("IF-C", url=url[0]),
                    InlineKeyboardButton("IF-D", url=url[1]),
                ]
            ]
        )
    elif link_key == "prak_basdat":
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("IF-B", url=url[0]),
                    InlineKeyboardButton("IF-C", url=url[1]),
                ]
            ]
        )
    else:
        return InlineKeyboardMarkup([[InlineKeyboardButton("SPADA", url=url)]])


async def send_absen(context: SpadaCtx, hari, link_key):
    reply_markup = (
        markup([Absen.links[f"{link_key}_b"], Absen.links[f"{link_key}_c"]], link_key)
        if link_key == "prak_basdat"
        else (
            markup(
                [Absen.links[f"{link_key}_c"], Absen.links[f"{link_key}_d"]], link_key
            )
            if link_key == "prak_alpro"
            else markup(Absen.links[link_key])
        )
    )

    await context.bot.send_message(
        context.GROUP,
        absen(hari, link_key),
        parse_mode=MD,
        reply_markup=reply_markup,
    )

    await context.bot.send_message(
        context.OWNER, f"Absen `{link_key}` berhasil terkirim\.", parse_mode=MD
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
        job_queue.run_daily(
            job_function,
            waktu(waktu_str),
            days=(day,),
            name=f"{hari.lower()}-{link_key}",
        )
