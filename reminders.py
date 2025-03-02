import logging
from datetime import datetime, time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.helpers import escape_markdown
from pytz import timezone
from classes import SpadaCtx, MD

logging.basicConfig()
logging.getLogger("apscheduler").setLevel(logging.DEBUG)


class Absen:
    schedule = [
        ("Senin", "Olahraga", "olahraga", "06:00", 1),
        ("Senin", "Alpro Lanjut", "alpro", "12:00", 1),
        ("Senin", "Prak Jarkom IF\-C", "prak_jarkom_c", "15:30", 1),
        ("Selasa", "MRV", "matriks", "07:00", 2),
        ("Selasa", "Statistika", "statistika", "09:30", 2),
        ("Selasa", "STI", "sti", "14:00", 2),
        ("Rabu", "Jarkom", "jarkom", "12:00", 3),
        ("Rabu", "Prak Jarkom IF\-D", "prak_jarkom_d", "15:30", 3),
        ("Kamis", "Prak Alpro IF\-D", "prak_alpro_d", "07:55", 4),
        ("Kamis", "Prak Alpro IF\-C", "prak_alpro_c", "10:00", 4),
        ("Kamis", "B\. Ing", "bing", "12:00", 4),
        ("Jumat", "Kalkulus Lanjut", "kalkulus", "07:00", 5),
    ]
    links = {
        "olahraga": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=637997",
        "prak_alpro_c": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=648277",
        "prak_alpro_d": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=646428",
        "prak_jarkom_c": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=646416",
        "prak_jarkom_d": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=648456",
        "alpro": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=652919",
        "matriks": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=644137",
        "statistika": "https://spada.upnyk.ac.id/mod/forum/view.php?id=636071",
        "sti": "https://spada.upnyk.ac.id/mod/attendance/view.php?id=644230",
        "jarkom": "https://spada.upnyk.ac.id/mod/forum/view.php?id=633273",
        "bing": "https://spada.upnyk.ac.id/course/view.php?id=36161",
        "kalkulus": "https://spada.upnyk.ac.id/course/view.php?id=36959",
    }
    waktu = {
        "olahraga": "06:00 \- 10:00",
        "prak_alpro_d": "07:55 \- 08:15",
        "prak_alpro_c": "10:00 \- 10:15",
        "alpro": "12:00 \- 13:45",
        "prak_jarkom_c": "15:30 \- 15:45",
        "prak_jarkom_d": "15:30 \- 15:45",
        "matriks": "07:00 \- 08:45",
        "statistika": "09:30 \- 12:00",
        "sti": "14:00 \- 17:00",
        "jarkom": "12:00 \- 14:30",
        "bing": "12:00 \- 13:45",
        "kalkulus": "07:00 \- 08:45",
    }

    @classmethod
    def get_matkul_info(cls, current_key):
        for i, item in enumerate(cls.schedule):
            if item[2] == current_key:
                current_title = item[1]
                current_time = cls.waktu[current_key]
                current_day = cls.schedule[i][4]
                try:
                    next_title = cls.schedule[i + 1][1]
                    next_key = cls.schedule[i + 1][2]
                    next_day = cls.schedule[i + 1][4]
                except:
                    next_day = 1
                    next_key = "olahraga"
                    next_title = "Olahraga"
                next_time = cls.waktu[next_key]
                curtime = datetime.strptime(current_time.split(" \- ")[0], "%H:%M")
                if "Tidak" not in next_time:
                    nexttime = datetime.strptime(next_time.split(" \- ")[0], "%H:%M")
                    next_time = next_time.split(" \- ")[0]
                    if curtime > nexttime:
                        if current_day + 1 == next_day:
                            next_time = f"{next_time} \(Besok\)"
                        else:
                            next_time = f"{next_time} \(Senin\)"
                return current_title, current_time, next_title, next_time


def waktu(jam):
    jam, menit = map(int, jam.split(":"))
    return time(jam, menit, tzinfo=timezone("Asia/Jakarta"))


def absen(hari, link_key):
    print(link_key)
    matkul, waktu, next_matkul, next_waktu = Absen.get_matkul_info(link_key)
    return (
        f"*Absen Hari {hari} Kelas IF\-B*\n\n"
        f"Matkul: *{matkul}*\n"
        f"Jam: *{waktu}*\n\n"
        f"Mata kuliah selanjutnya: *{next_matkul}*\n"
        # f"{'Jam: ' if next_matkul != 'Pendidikan Agama Islam' else ''}*{next_waktu}*\n\n"
        f"Jam: *{next_waktu}*\n\n"
        f"*__Perhatikan waktu absennya\! Jangan menunda\-nunda\.__*"
    )


def markup(url, link_key):
    return InlineKeyboardMarkup([[InlineKeyboardButton("SPADA", url=url)]])


async def send_absen(context: SpadaCtx, hari, link_key):
    await context.bot.send_message(
        context.GROUP,
        absen(hari, link_key),
        parse_mode=MD,
        reply_markup=markup(Absen.links[link_key], link_key),
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
