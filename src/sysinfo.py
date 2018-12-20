#!/usr/bin/env python

"""
Started out as a simple script to output information about the system,
but I got carried away :)
"""

from __future__ import print_function

import argparse
import datetime
import os
import platform
import psutil
import socket
import sys
import time

from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM

from uptime import uptime
from uptime import boottime

import pprint


def human_size(size_bytes, a_kilobyte_is_1024_bytes=True):
    """
    format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB, EB, ZB, YB
    Note that by default, bytes/KB will be reported in whole numbers but MB and above will have greater precision
    e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc
    """

    suffixes_table = {1000: [('bytes', 0), ('KB', 0), ('MB', 1), ('GB', 2), ('TB', 2), ('PB', 2), ('EB', 2), ('ZB', 2), ('YB', 2)],
                      1024: [('bytes', 0), ('KiB', 0), ('MiB', 1), ('GiB', 2), ('TiB', 2), ('PiB', 2), ('EiB', 2), ('ZiB', 2), ('YiB', 2)]}

    if size_bytes < 0:
        return "Unknown"

    if size_bytes == 1:
        return "1 byte"

    multiple = 1024 if a_kilobyte_is_1024_bytes else 1000

    num = float(size_bytes)
    for suffix, precision in suffixes_table[multiple]:
        if num < multiple:
            break
        num /= multiple

    if precision == 0:
        formatted_size = "%d" % num
    else:
        formatted_size = str(round(num, ndigits=precision))

    return "%s %s" % (formatted_size, suffix)


def secs2hours(secs):
    """
    Convert the number of seconds into hours, mintues and seconds (digital format)
    """

    if secs < 0:
        return "Unknown"

    mm, ss = divmod(secs, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d" % (hh, mm, ss)


def seconds_to_days(secs):
    """
    Convert the number of seconds into days, hours, mintues and seconds (string format)
    """
    parts = []

    days, secs = secs // 86400, secs % 86400
    if days:
        parts.append('%d day%s' % (days, 's' if days != 1 else ''))

    hours, secs = secs // 3600, secs % 3600
    if hours:
        parts.append('%d hour%s' % (hours, 's' if hours != 1 else ''))

    minutes, secs = secs // 60, secs % 60
    if minutes:
        parts.append('%d minute%s' % (minutes, 's' if minutes != 1 else ''))

    if secs or not parts:
        parts.append('%.2f seconds' % secs)

    return ', '.join(parts)


def battery_info():
    """
    Battery Information
    """
    if not hasattr(psutil, "sensors_battery"):
        print("platform not supported")
        return 0
    batt = psutil.sensors_battery()
    if batt is None:
        print("no battery is installed")
        return 0

    print("charge:     %s%%" % round(batt.percent, 2))
    if batt.power_plugged:
        print("status:     %s" % (
            "charging" if batt.percent < 100 else "fully charged"))
        print("plugged in: yes")
    else:
        print("left:       %s" % seconds_to_days(batt.secsleft))
        print("status:     %s" % "discharging")
        print("plugged in: no")


def cpu_info():
    """
    CPU Information
    """
    freq = psutil.cpu_freq()

    print("CPUs: %d" % psutil.cpu_count())

    if freq is not None:
        print("Frequency: Current (%s), Min (%s), Max (%s)" % (freq.current, freq.min, freq.max))


def disk_info():
    """
    Disk Information
    """

    templ = "%-17s %10s %10s %10s %5s%% %9s  %s"
    print(templ % ("Device", "Total", "Used", "Free", "Use ", "Type",
                   "Mount"))
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue
        usage = psutil.disk_usage(part.mountpoint)
        print(templ % (
            part.device,
            human_size(usage.total),
            human_size(usage.used),
            human_size(usage.free),
            int(usage.percent),
            part.fstype,
            part.mountpoint))


def fan_info():
    """
    Fan Information
    """

    if not hasattr(psutil, "sensors_fans"):
        print("platform not supported")
        return
    fans = psutil.sensors_fans()
    if not fans:
        print("no fans detected")
        return
    for name, entries in fans.items():
        print(name)
        for entry in entries:
            print("    %-20s %s RPM" % (entry.label or name, entry.current))


def free_memory_info():
    """
    Free Memory Information
    """
    virt = psutil.virtual_memory()
    swap = psutil.swap_memory()
    templ = "%-7s %10s %10s %10s %10s %10s %10s"
    print(templ % ('', 'total', 'used', 'free', 'shared', 'buffers', 'cache'))
    print(templ % (
        'Mem:',
        int(virt.total / 1024),
        int(virt.used / 1024),
        int(virt.free / 1024),
        int(getattr(virt, 'shared', 0) / 1024),
        int(getattr(virt, 'buffers', 0) / 1024),
        int(getattr(virt, 'cached', 0) / 1024)))
    print(templ % (
        'Swap:', int(swap.total / 1024),
        int(swap.used / 1024),
        int(swap.free / 1024),
        '',
        '',
        ''))


def load_average():
    """
    Load Average Information
    """
    a = os.getloadavg()
    print('Load: %s, %s, %s' % (round(a[0], 2), round(a[1], 2), round(a[2], 2)))


def pprint_ntuple(nt):
    """
    Print a Tuple
    """
    for name in nt._fields:
        value = getattr(nt, name)
        if name != 'percent':
            value = human_size(value)
        print('%-10s : %7s' % (name.capitalize(), value))


def memory_info():
    """
    """
    print('MEMORY\n------')
    pprint_ntuple(psutil.virtual_memory())
    print('\nSWAP\n----')
    pprint_ntuple(psutil.swap_memory())


def netstat_info():
    """
    Netstat Information
    """
    AD = "-"
    AF_INET6 = getattr(socket, 'AF_INET6', object())
    proto_map = {
        (AF_INET, SOCK_STREAM): 'tcp',
        (AF_INET6, SOCK_STREAM): 'tcp6',
        (AF_INET, SOCK_DGRAM): 'udp',
        (AF_INET6, SOCK_DGRAM): 'udp6',
    }

    if not os.geteuid() == 0:
        print("This option requires root permissions")
        return 0

    templ = "%-5s %-30s %-30s %-13s %-6s %s"
    print(templ % (
        "Proto", "Local address", "Remote address", "Status", "PID",
        "Program name"))
    proc_names = {}
    for p in psutil.process_iter(attrs=['pid', 'name']):
        proc_names[p.info['pid']] = p.info['name']
    for c in psutil.net_connections(kind='inet'):
        laddr = "%s:%s" % (c.laddr)
        raddr = ""
        if c.raddr:
            raddr = "%s:%s" % (c.raddr)
        print(templ % (
            proto_map[(c.family, c.type)],
            laddr,
            raddr or AD,
            c.status,
            c.pid or AD,
            proc_names.get(c.pid, '?')[:15],
        ))


def network_info():
    """
    Network Information
    """

    af_map = {
        socket.AF_INET: 'IPv4',
        socket.AF_INET6: 'IPv6',
        psutil.AF_LINK: 'MAC',
    }

    duplex_map = {
        psutil.NIC_DUPLEX_FULL: "full",
        psutil.NIC_DUPLEX_HALF: "half",
        psutil.NIC_DUPLEX_UNKNOWN: "?",
    }

    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)
    for nic, addrs in psutil.net_if_addrs().items():
        print("%s:" % (nic))
        if nic in stats:
            st = stats[nic]
            print("    stats          : ", end='')
            print("speed=%sMB, duplex=%s, mtu=%s, up=%s" % (
                st.speed, duplex_map[st.duplex], st.mtu,
                "yes" if st.isup else "no"))
        if nic in io_counters:
            io = io_counters[nic]
            print("    incoming       : ", end='')
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                human_size(io.bytes_recv), io.packets_recv, io.errin,
                io.dropin))
            print("    outgoing       : ", end='')
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                human_size(io.bytes_sent), io.packets_sent, io.errout,
                io.dropout))
        for addr in addrs:
            print("    %-4s" % af_map.get(addr.family, addr.family), end="")
            print(" address   : %s" % addr.address)
            if addr.broadcast:
                print("         broadcast : %s" % addr.broadcast)
            if addr.netmask:
                print("         netmask   : %s" % addr.netmask)
            if addr.ptp:
                print("      p2p       : %s" % addr.ptp)
        print("")


def operating_system_info():
    """
    Operating System Information
    """
    print('Normal : %s' % platform.platform())
    print('Aliased: %s' % platform.platform(aliased=True))
    print('Terse  : %s' % platform.platform(terse=True))

    print('system   : %s' % platform.system())
    print('node     : %s' % platform.node())
    print('release  : %s' % platform.release())
    print('version  : %s' % platform.version())
    print('machine  : %s' % platform.machine())
    print('processor: %s' % platform.processor())


def process_info():
    """
    Process Information
    """

    PROC_STATUSES_RAW = {
        psutil.STATUS_RUNNING: "R",
        psutil.STATUS_SLEEPING: "S",
        psutil.STATUS_DISK_SLEEP: "D",
        psutil.STATUS_STOPPED: "T",
        psutil.STATUS_TRACING_STOP: "t",
        psutil.STATUS_ZOMBIE: "Z",
        psutil.STATUS_DEAD: "X",
        psutil.STATUS_WAKING: "WA",
        psutil.STATUS_IDLE: "I",
        psutil.STATUS_LOCKED: "L",
        psutil.STATUS_WAITING: "W",
    }

    if hasattr(psutil, 'STATUS_WAKE_KILL'):
        PROC_STATUSES_RAW[psutil.STATUS_WAKE_KILL] = "WK"

    if hasattr(psutil, 'STATUS_SUSPENDED'):
        PROC_STATUSES_RAW[psutil.STATUS_SUSPENDED] = "V"

    today_day = datetime.date.today()
    templ = "%-10s %5s %4s %4s %7s %7s %-13s %-5s %5s %7s  %s"
    attrs = ['pid', 'cpu_percent', 'memory_percent', 'name', 'cpu_times',
             'create_time', 'memory_info', 'status']
    if os.name == 'posix':
        attrs.append('uids')
        attrs.append('terminal')
    print(templ % ("USER", "PID", "%CPU", "%MEM", "VSZ", "RSS", "TTY",
                   "STAT", "START", "TIME", "COMMAND"))
    for p in psutil.process_iter():
        try:
            pinfo = p.as_dict(attrs, ad_value='')
        except psutil.NoSuchProcess:
            pass
        else:
            if pinfo['create_time']:
                ctime = datetime.datetime.fromtimestamp(pinfo['create_time'])
                if ctime.date() == today_day:
                    ctime = ctime.strftime("%H:%M")
                else:
                    ctime = ctime.strftime("%b%d")
            else:
                ctime = ''
            cputime = time.strftime("%M:%S",
                                    time.localtime(sum(pinfo['cpu_times'])))
            try:
                user = p.username()
            except KeyError:
                if os.name == 'posix':
                    if pinfo['uids']:
                        user = str(pinfo['uids'].real)
                    else:
                        user = ''
                else:
                    raise
            except psutil.Error:
                user = ''
            if os.name == 'nt' and '\\' in user:
                user = user.split('\\')[1]
            vms = pinfo['memory_info'] and \
                int(pinfo['memory_info'].vms / 1024) or '?'
            rss = pinfo['memory_info'] and \
                int(pinfo['memory_info'].rss / 1024) or '?'
            memp = pinfo['memory_percent'] and \
                round(pinfo['memory_percent'], 1) or '?'
            status = PROC_STATUSES_RAW.get(pinfo['status'], pinfo['status'])
            print(templ % (
                user[:10],
                pinfo['pid'],
                pinfo['cpu_percent'],
                memp,
                vms,
                rss,
                pinfo.get('terminal', '') or '?',
                status,
                ctime,
                cputime,
                pinfo['name'].strip() or '?'))


def sensor_info():
    """
    Sensor Information
    """
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
    else:
        temps = {}
    if hasattr(psutil, "sensors_fans"):
        fans = psutil.sensors_fans()
    else:
        fans = {}
    if hasattr(psutil, "sensors_battery"):
        battery = psutil.sensors_battery()
    else:
        battery = None

    if not any((temps, fans, battery)):
        print("can't read any temperature, fans or battery info")
        return

    names = set(list(temps.keys()) + list(fans.keys()))
    for name in names:
        print(name)
        # Temperatures.
        if name in temps:
            print("    Temperatures:")
            for entry in temps[name]:
                print("        %-20s %s C (high=%sC, critical=%sC)" % (
                    entry.label or name, entry.current, entry.high,
                    entry.critical))
        # Fans.
        if name in fans:
            print("    Fans:")
            for entry in fans[name]:
                print("        %-20s %s RPM" % (
                    entry.label or name, entry.current))

    # Battery.
    if battery:
        print("Battery:")
        print("    charge:     %s%%" % round(battery.percent, 2))
        if battery.power_plugged:
            print("    status:     %s" % (
                "charging" if battery.percent < 100 else "fully charged"))
            print("    plugged in: yes")
        else:
            print("    left:       %s" % seconds_to_days(battery.secsleft))
            print("    status:     %s" % "discharging")
            print("    plugged in: no")


def temperature_info():
    """
    Temperature Information
    """
    if not hasattr(psutil, "sensors_temperatures"):
        print("platform not supported")
        return 1
    temps = psutil.sensors_temperatures()
    if not temps:
        print("can't read any temperature")
        return 1
    for name, entries in temps.items():
        print(name)
        for entry in entries:
            print("    %-20s %s C (high = %s C, critical = %s C)" % (
                entry.label or name, entry.current, entry.high,
                entry.critical))


def uptime_info():
    """
    Uptime Information
    """

    print('Uptime: %s.' % seconds_to_days(uptime()))
    print('Booted: %s' % boottime().strftime('%c'))


def summary_info():
    """
    Summary Information
    """

    disk_parts = []
    nic_parts = []

    virt = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disks = psutil.disk_partitions()
    nics = psutil.net_io_counters(pernic=True)
    freq = psutil.cpu_freq()

    for disk in disks:
        disk_parts.append(disk.mountpoint)

    for nic in nics:
        nic_parts.append(nic)

    print('Uptime:    %s (Booted: %s)' % (seconds_to_days(uptime()), boottime().strftime('%c')))

    if freq is not None:
        print("CPUs: %d (Frequency - Current (%s), Min (%s), Max (%s))" % (psutil.cpu_count(), freq.current, freq.min, freq.max))
    else:
        print('CPUs:      %s' % psutil.cpu_count())

    print('Memory:    Total %s, Available %s, Free %.2f %%' % (human_size(virt.total), human_size(virt.available), (100 - virt.percent)))
    print('Swap:      Total %s, Available %s, Free %.2f %%' % (human_size(swap.total), human_size(swap.free), (100 - swap.percent)))
    print('Disks:     %s (%s)' % (len(disks), ", ".join(disk_parts)))
    print('NICs:      %s (%s)' % (len(nics), ", ".join(nic_parts)))
    print('Processes: %s' % len(psutil.pids()))


def main(cmdline=None):

    """
    The main function. This takes the command line arguments provided, parsers them.
    """

    parser = make_parser()

    if len(cmdline) == 0:
        parser.print_help(sys.stderr)
        return 1

    args = parser.parse_args(cmdline)

    if args.battery:
        battery_info()

    if args.cpu:
        cpu_info()

    if args.disk:
        disk_info()

    if args.fans:
        fan_info()

    if args.free_memory:
        free_memory_info()

    if args.load:
        load_average()

    if args.memory:
        memory_info()

    if args.network:
        network_info()

    if args.netstat:
        netstat_info()

    if args.operating_system:
        operating_system_info()

    if args.processes:
        process_info()

    if args.sensors:
        sensor_info()

    if args.temperature:
        temperature_info()

    if args.uptime:
        uptime_info()

    if args.summary:
        summary_info()

    return 0


def make_parser():

    """
    This function builds up the command line parser that is used by the script.
    """

    parser = argparse.ArgumentParser(description='SysInfo')

    parser.add_argument('-b', '--battery', help='Show all batttery information', action="store_true")
    parser.add_argument('-c', '--cpu', help='Show all cpu information', action="store_true")
    parser.add_argument('-d', '--disk', help='Show all disk information', action="store_true")
    parser.add_argument('-F', '--fans', help='Show all fan information', action="store_true")
    parser.add_argument('-f', '--free-memory', help='Show all memory information', action="store_true")
    parser.add_argument('-l', '--load', help='Show all load information', action="store_true")
    parser.add_argument('-m', '--memory', help='Show all memory information', action="store_true")
    parser.add_argument('-n', '--network', help='Show all network information', action="store_true")
    parser.add_argument('-N', '--netstat', help='Show all netstat information', action="store_true")
    parser.add_argument('-o', '--operating-system', help='Show all operating system information', action="store_true")
    parser.add_argument('-p', '--processes', help='Show all process information', action="store_true")
    parser.add_argument('-s', '--sensors', help='Show all sensor information', action="store_true")
    parser.add_argument('-t', '--temperature', help='Show all temperature information', action="store_true")
    parser.add_argument('-u', '--uptime', help='Show all uptime information', action="store_true")
    parser.add_argument('-S', '--summary', help='A summary overview', action="store_true")

    return parser


if __name__ == "__main__":

    # This runs when the application is run from the command it grabs sys.argv[1:] which is everything after
    # the program name and passes it to main the return value from main is then used as the argument to
    # sys.exit, which you can test for in the shell. program exit codes are usually 0 for ok, and non-zero
    # for something going wrong.

    sys.exit(main(sys.argv[1:]))
