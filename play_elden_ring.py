import os
import re
import json
import time
import wave
import time
import base64
import random
import shutil
import secrets
import hashlib
import datetime
import binascii
import subprocess
import moviepy.editor as mp
from pydub import AudioSegment
from pynput import keyboard as kb
from WindowManager import WindowMgr
from flask import Flask, request, Response


def get_hp(lvl):

    hp = {
        1: 300,
        2: 304,
        3: 312,
        4: 322,
        5: 334,
        6: 347,
        7: 362,
        8: 378,
        9: 396,
        10: 414,
        11: 434,
        12: 455,
        13: 476,
        14: 499,
        15: 522,
        16: 547,
        17: 572,
        18: 598,
        19: 624,
        20: 652,
        21: 680,
        22: 709,
        23: 738,
        24: 769,
        25: 800,
        26: 833,
        27: 870,
        28: 910,
        29: 951,
        30: 994,
        31: 1037,
        32: 1081,
        33: 1125,
        34: 1170,
        35: 1216,
        36: 1262,
        37: 1308,
        38: 1355,
        39: 1402,
        40: 1450,
        41: 1476,
        42: 1503,
        43: 1529,
        44: 1555,
        45: 1581,
        46: 1606,
        47: 1631,
        48: 1656,
        49: 1680,
        50: 1704,
        51: 1727,
        52: 1750,
        53: 1772,
        54: 1793,
        55: 1814,
        56: 1834,
        57: 1853,
        58: 1871,
        59: 1887,
        60: 1900,
        61: 1906,
        62: 1912,
        63: 1918,
        64: 1924,
        65: 1930,
        66: 1936,
        67: 1942,
        68: 1948,
        69: 1954,
        70: 1959,
        71: 1965,
        72: 1971,
        73: 1977,
        74: 1982,
        75: 1988,
        76: 1993,
        77: 1999,
        78: 2004,
        79: 2010,
        80: 2015,
        81: 2020,
        82: 2026,
        83: 2031,
        84: 2036,
        85: 2041,
        86: 2046,
        87: 2051,
        88: 2056,
        89: 2060,
        90: 2065,
        91: 2070,
        92: 2074,
        93: 2078,
        94: 2082,
        95: 2086,
        96: 2090,
        97: 2094,
        98: 2097,
        99: 2100,
    }
    return hp.get(lvl)


def get_fp(lvl):

    fp = {
        1: 40,
        2: 43,
        3: 46,
        4: 49,
        5: 52,
        6: 55,
        7: 58,
        8: 62,
        9: 65,
        10: 68,
        11: 71,
        12: 74,
        13: 77,
        14: 81,
        15: 84,
        16: 87,
        17: 90,
        18: 93,
        19: 96,
        20: 100,
        21: 106,
        22: 112,
        23: 118,
        24: 124,
        25: 130,
        26: 136,
        27: 142,
        28: 148,
        29: 154,
        30: 160,
        31: 166,
        32: 172,
        33: 178,
        34: 184,
        35: 190,
        36: 196,
        37: 202,
        38: 208,
        39: 214,
        40: 220,
        41: 226,
        42: 232,
        43: 238,
        44: 244,
        45: 250,
        46: 256,
        47: 262,
        48: 268,
        49: 274,
        50: 280,
        51: 288,
        52: 297,
        53: 305,
        54: 313,
        55: 321,
        56: 328,
        57: 335,
        58: 341,
        59: 346,
        60: 350,
        61: 352,
        62: 355,
        63: 357,
        64: 360,
        65: 362,
        66: 365,
        67: 367,
        68: 370,
        69: 373,
        70: 375,
        71: 378,
        72: 380,
        73: 383,
        74: 385,
        75: 388,
        76: 391,
        77: 393,
        78: 396,
        79: 398,
        80: 401,
        81: 403,
        82: 406,
        83: 408,
        84: 411,
        85: 414,
        86: 416,
        87: 419,
        88: 421,
        89: 424,
        90: 426,
        91: 429,
        92: 432,
        93: 434,
        94: 437,
        95: 439,
        96: 442,
        97: 444,
        98: 447,
        99: 450,
    }
    return fp.get(lvl)


def get_st(lvl):

    stamina = {
        1: 80,
        2: 81,
        3: 82,
        4: 84,
        5: 85,
        6: 87,
        7: 88,
        8: 90,
        9: 91,
        10: 92,
        11: 94,
        12: 95,
        13: 97,
        14: 98,
        15: 100,
        16: 101,
        17: 103,
        18: 105,
        19: 106,
        20: 108,
        21: 110,
        22: 111,
        23: 113,
        24: 115,
        25: 116,
        26: 118,
        27: 120,
        28: 121,
        29: 123,
        30: 125,
        31: 126,
        32: 128,
        33: 129,
        34: 131,
        35: 132,
        36: 134,
        37: 135,
        38: 137,
        39: 138,
        40: 140,
        41: 141,
        42: 143,
        43: 144,
        44: 146,
        45: 147,
        46: 149,
        47: 150,
        48: 152,
        49: 153,
        50: 155,
        51: 155,
        52: 155,
        53: 155,
        54: 156,
        55: 156,
        56: 156,
        57: 157,
        58: 157,
        59: 157,
        60: 158,
        61: 158,
        62: 158,
        63: 158,
        64: 159,
        65: 159,
        66: 159,
        67: 160,
        68: 160,
        69: 160,
        70: 161,
        71: 161,
        72: 161,
        73: 162,
        74: 162,
        75: 162,
        76: 162,
        77: 163,
        78: 163,
        79: 163,
        80: 164,
        81: 164,
        82: 164,
        83: 165,
        84: 165,
        85: 165,
        86: 166,
        87: 166,
        88: 166,
        89: 166,
        90: 167,
        91: 167,
        92: 167,
        93: 168,
        94: 168,
        95: 168,
        96: 169,
        97: 169,
        98: 169,
        99: 170,
    }
    return stamina.get(lvl)


def l_endian(val):
    """Takes bytes and returns little endian int32/64"""
    l_hex = bytearray(val)
    l_hex.reverse()
    str_l = "".join(format(i, "02x") for i in l_hex)
    return int(str_l, 16)


def recalc_checksum(file):
    with open(file, "rb") as fh:
        dat = fh.read()
        slot_ls = []
        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300

        # Build nested list containing data and checksum related to each slot
        for i in range(10):
            # [ dat[0x00000310:0x0028030F +1], dat[ 0x00000300:0x0000030F + 1] ]
            d = dat[s_ind : s_ind + slot_len + 1]
            c = dat[c_ind : c_ind + cs_len + 1]
            slot_ls.append([d, c])
            s_ind += 2621456
            c_ind += 2621456

        # Do comparisons and recalculate checksums
        for ind, i in enumerate(slot_ls):
            new_cs = hashlib.md5(i[0]).hexdigest()
            cur_cs = binascii.hexlify(i[1]).decode("utf-8")

            if new_cs != cur_cs:
                slot_ls[ind][1] = binascii.unhexlify(new_cs)

        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300
        # Insert all checksums into data
        for i in slot_ls:
            dat = dat[:s_ind] + i[0] + dat[s_ind + slot_len + 1 :]
            dat = dat[:c_ind] + i[1] + dat[c_ind + cs_len + 1 :]
            s_ind += 2621456
            c_ind += 2621456

        # Manually doing General checksum
        general = dat[0x019003B0 : 0x019603AF + 1]
        new_cs = hashlib.md5(general).hexdigest()
        cur_cs = binascii.hexlify(dat[0x019003A0 : 0x019003AF + 1]).decode("utf-8")

        writeval = binascii.unhexlify(new_cs)
        dat = dat[:0x019003A0] + writeval + dat[0x019003AF + 1 :]

        with open(file, "wb") as fh1:
            fh1.write(dat)


def change_name(file, nw_nm, dest_slot):
    """Builds list of each character name from static name locations in header, then passes specified char name in bytes into replacer function."""

    def replacer(file, old_name, name):
        """Scans for all occurences of old_name and replaces it with name."""
        with open(file, "rb") as fh:
            dat1 = fh.read()
            id_loc = []
            index = 0

            while index < len(dat1):
                index = dat1.find(
                    old_name.rstrip(b"\x00"), index
                )  # Strip empty bytes off of character name

                if index == -1:
                    break
                id_loc.append(index)
                if (
                    len(id_loc) > 300
                ):  # If it found that many locations then the name might be short like "M"
                    return "error"
                index += 8

            nw_nm_bytes = name.encode("utf-16")[2:]

            num = 32 - len(nw_nm_bytes)
            for i in range(num):
                nw_nm_bytes = nw_nm_bytes + b"\x00"

            for i in id_loc:
                fh.seek(0)
                a = fh.read(i)
                b = nw_nm_bytes
                fh.seek(i + 32)
                c = fh.read()
                data = a + b + c

                with open(file, "wb") as f:
                    f.write(data)
        recalc_checksum(file)

    # empty = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    with open(file, "rb") as fh:
        dat1 = fh.read()

    name_locations = []
    ind1 = 0x1901D0E  # Start address of char names in header, 588 bytes apart
    for i in range(10):
        nm = dat1[ind1 : ind1 + 32]
        name_locations.append(nm)  # Name in bytes
        ind1 += 588

    x = replacer(file, name_locations[dest_slot - 1], nw_nm)
    return x


def replace_id(file, newid):
    id_loc = []
    index = 0

    with open(file, "rb") as f:
        dat = f.read()
        f.seek(26215348)  # start address of steamID
        steam_id = f.read(8)  # Get steamID

        id_loc = []
        index = 0
        while index < len(dat):
            index = dat.find(steam_id, index)
            if index == -1:
                break
            id_loc.append(index)
            index += 8

        for i in id_loc:
            f.seek(0)
            a = f.read(i)
            b = newid.to_bytes(8, "little")
            f.seek(i + 8)
            c = f.read()
            data = a + b + c

            with open(file, "wb") as fh:
                fh.write(data)

    recalc_checksum(file)


def copy_save(src_file, dest_file, src_char, dest_char):
    """Copy characters between save files"""
    slot_len = 2621456
    lvls = get_levels(src_file)
    lvl = lvls[src_char - 1]

    with open(src_file, "rb") as fh:
        dat = fh.read()

    if src_char == 1:
        src_slot = dat[0x00000310 : 0x0028030F + 1]
    else:
        src_slot = dat[
            0x00000310
            + (src_char - 1) * slot_len : (0x0028030F + ((src_char - 1) * slot_len))
            + 1
        ]

    with open(dest_file, "rb") as fh:
        dat1 = fh.read()

    if dest_char == 1:
        slot_s = dat1[:0x00000310]
        slot_e = dat1[0x0028030F + 1 :]
    else:
        slot_s = dat1[: 0x00000310 + ((dest_char - 1) * slot_len)]
        slot_e = dat1[0x0028030F + ((dest_char - 1) * slot_len) + 1 :]

    dat1 = slot_s + src_slot + slot_e

    with open(dest_file, "wb") as fh:
        fh.write(dat1)

    set_level(dest_file, dest_char, lvl)


def get_id(file):
    with open(file, "rb") as f:
        dat = f.read()
        f.seek(26215348)  # start address of steamID
        steam_id = f.read(8)  # Get steamID
    return l_endian(steam_id)


def get_names(file):
    try:
        with open(file, "rb") as fh:
            dat1 = fh.read()

    except FileNotFoundError as e:
        return False
#    except FileNotFoundError as e:
#        d = file.split("/")[:4]
#        d = "/".join(d)

#        dir_id = re.findall(r'\d{17}',str(os.listdir(d)))
#        if len(dir_id) != 1:
#            return False

#        new_path = f"{d}/{dir_id[0]}/ER0000.sl2"
#        with open(new_path, "rb") as fh:
#            dat1 = fh.read()

    name1 = dat1[0x1901d0e:0x1901d0e + 32].decode('utf-16')
    name2 = dat1[0x1901f5a:0x1901f5a + 32].decode('utf-16')
    name3 = dat1[0x19021a6:0x19021a6 + 32].decode('utf-16')
    name4 = dat1[0x19023f2 :0x19023f2  +32].decode('utf-16')
    name5 = dat1[0x190263e :0x190263e  +32].decode('utf-16')
    name6 = dat1[0x190288a :0x190288a  +32].decode('utf-16')
    name7 = dat1[0x1902ad6 :0x1902ad6  +32].decode('utf-16')
    name8 = dat1[0x1902d22 :0x1902d22  +32].decode('utf-16')
    name9 = dat1[0x1902f6e :0x1902f6e  +32].decode('utf-16')
    name10 = dat1[0x19031ba :0x19031ba  +32].decode('utf-16')


    names = [name1,name2,name3,name4,name5,name6,name7,name8,name9,name10]


    for ind,i in enumerate(names):
        if i == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
            names[ind] = None

    for ind,i in enumerate(names):
        if not i is None:
            names[ind] = i.split('\x00')[0] # name looks like this: 'wete\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    return names


def random_str():
    """Generates random 16 character long name"""
    val = range(random.randint(900, 900000))
    hashed = hashlib.sha1(str(val).encode())
    random_name = base64.urlsafe_b64encode(hashed.digest()[:12])
    return random_name.decode("utf-8")


def get_slot_ls(file):
    with open(file, "rb") as fh:
        dat = fh.read()

        slot1 = dat[0x00000310 : 0x0028030F + 1]  # SLOT 1
        slot2 = dat[0x00280320 : 0x050031F + 1]
        slot3 = dat[0x500330 : 0x78032F + 1]
        slot4 = dat[0x780340 : 0xA0033F + 1]
        slot5 = dat[0xA00350 : 0xC8034F + 1]
        slot6 = dat[0xC80360 : 0xF0035F + 1]
        slot7 = dat[0xF00370 : 0x118036F + 1]
        slot8 = dat[0x1180380 : 0x140037F + 1]
        slot9 = dat[0x1400390 : 0x168038F + 1]
        slot10 = dat[0x16803A0 : 0x190039F + 1]
        return [slot1, slot2, slot3, slot4, slot5, slot6, slot7, slot8, slot9, slot10]


def get_slot_slices(file):
    with open(file, "rb") as fh:
        dat = fh.read()

    slot1_start = dat[:0x00000310]
    slot1_end = dat[0x0028030F + 1 :]

    slot2_start = dat[:0x00280320]
    slot2_end = dat[0x050031F + 1 :]

    slot3_start = dat[:0x500330]
    slot3_end = dat[0x78032F + 1 :]

    slot4_start = dat[:0x780340]
    slot4_end = dat[0xA0033F + 1 :]

    slot5_start = dat[:0xA00350]
    slot5_end = dat[0xC8034F + 1 :]

    slot6_start = dat[:0xC80360]
    slot6_end = dat[0xF0035F + 1 :]

    slot7_start = dat[:0xF00370]
    slot7_end = dat[0x118036F + 1 :]

    slot8_start = dat[:0x1180380]
    slot8_end = dat[0x140037F + 1 :]

    slot9_start = dat[:0x1400390]
    slot9_end = dat[0x168038F + 1 :]

    slot10_start = dat[:0x16803A0]
    slot10_end = dat[0x190039F + 1 :]

    return [
        [slot1_start, slot1_end],
        [slot2_start, slot2_end],
        [slot3_start, slot3_end],
        [slot4_start, slot4_end],
        [slot5_start, slot5_end],
        [slot6_start, slot6_end],
        [slot7_start, slot7_end],
        [slot8_start, slot8_end],
        [slot9_start, slot9_end],
        [slot10_start, slot10_end],
    ]


def set_stats(file, char_num, stat_ls):

    locs = get_stats(file, char_num)[1]  # list of index values of stats

    index = 0
    for loc in locs:  # last val is lvl
        slots = get_slot_ls(file)
        slot_slices = get_slot_slices(file)
        dest_char = slots[char_num - 1]

        if index == 8:
            # Last val is lvl index
            lvl_ind = loc

            level = dest_char[lvl_ind : lvl_ind + 1]
            new_lv = sum(stat_ls) - 79
            new_lvl_int = new_lv
            new_lv = new_lv.to_bytes(2, "little")
            data = (
                slot_slices[char_num - 1][0]
                + dest_char[:lvl_ind]
                + new_lv
                + dest_char[lvl_ind + 2 :]
                + slot_slices[char_num - 1][1]
            )
            with open(file, "wb") as fh:
                fh.write(data)
            break

        writeval = stat_ls[index].to_bytes(1, "little")
        # total = dat[:0x00000310] + slot[:47496] + b'c' + slot[47496 +1:] + dat[0x0028030F +1:]
        data = (
            slot_slices[char_num - 1][0]
            + dest_char[:loc]
            + writeval
            + dest_char[loc + 1 :]
            + slot_slices[char_num - 1][1]
        )
        with open(file, "wb") as fh:
            fh.write(data)
        index += 1

    set_level(file, char_num, new_lvl_int)


def get_stats(file, char_slot):
    """"""
    # print(file, char_slot)
    lvls = get_levels(file)
    lv = lvls[char_slot - 1]
    slots = get_slot_ls(file)

    start_ind = 0
    slot1 = slots[char_slot - 1]
    indexes = []
    for ind, b in enumerate(slot1):
        if ind > 60000:
            return None
        try:
            stats = [
                l_endian(slot1[ind : ind + 1]),
                l_endian(slot1[ind + 4 : ind + 5]),
                l_endian(slot1[ind + 8 : ind + 9]),
                l_endian(slot1[ind + 12 : ind + 13]),
                l_endian(slot1[ind + 16 : ind + 17]),
                l_endian(slot1[ind + 20 : ind + 21]),
                l_endian(slot1[ind + 24 : ind + 25]),
                l_endian(slot1[ind + 28 : ind + 29]),
            ]
            hp = l_endian(slot1[ind - 44 : ind - 40])

            if sum(stats) == lv + 79 and l_endian(slot1[ind + 44 : ind + 46]) == lv:
                start_ind = ind
                lvl_ind = ind + 44
                break

        except:
            continue

    idx = ind
    for i in range(8):
        indexes.append(idx)
        idx += 4

    indexes.append(lvl_ind)  # Add the level location to the end o

    fp = []
    fp_inds = []
    y = start_ind - 32

    for i in range(3):
        fp.append(l_endian(slot1[y : y + 2]))
        fp_inds.append(y)
        y += 4

    hp = []
    hp_inds = []
    x = start_ind - 44

    for i in range(3):
        hp.append(l_endian(slot1[x : x + 2]))
        hp_inds.append(x)
        x += 4

    stam = []
    stam_inds = []
    z = start_ind - 16

    for i in range(3):
        stam.append(l_endian(slot1[z : z + 2]))
        stam_inds.append(z)
        z += 4

    return [
        stats,
        indexes,
        hp_inds,
        stam_inds,
        fp_inds,
    ]  # [[36, 16, 38, 33, 16, 9, 10, 7], 47421]

    # DELETE THIS ON NEXT RELEASE
    hp = []
    hp_inds = []
    x = start_ind - 44
    for i in range(3):
        hp.append(l_endian(slot1[x : x + 2]))
        hp_inds.append(x)
        x += 4

    return [
        stats,
        indexes,
        hp_inds,
    ]  # [[36, 16, 38, 33, 16, 9, 10, 7], [47421,47421], [3534345,35345,35345]]
    # END


def set_level(file, char, lvl):
    """Sets levels in static header position by char names for in-game load save menu."""
    locs = [
        26221872,
        26222460,
        26223048,
        26223636,
        26224224,
        26224812,
        26225400,
        26225988,
        26226576,
        26227164,
    ]
    with open(file, "rb") as fh:
        dat = fh.read()
        a = dat[: locs[char - 1]]
        b = lvl.to_bytes(2, "little")
        c = dat[locs[char - 1] + 2 :]
        data = a + b + c

    with open(file, "wb") as f:
        f.write(data)
    recalc_checksum(file)


def get_levels(file):
    with open(file, "rb") as fh:
        dat = fh.read()

    ind = 0x1901D0E + 34
    lvls = []
    for i in range(10):
        l = dat[ind : ind + 2]

        lvls.append(l_endian(l))
        ind += 588
    return lvls


def set_attributes(file, slot, lvls, custom_val=False):

    stats = get_stats(file, slot)

    hp_inds = stats[2]
    hp_val = get_hp(lvls[0])

    fp_inds = stats[3]
    fp_val = get_fp(lvls[1])

    st_inds = stats[4]
    st_val = get_st(lvls[2])

    char_slot = get_slot_ls(file)[slot - 1]
    dat_slices = get_slot_slices(file)[slot - 1]

    all_inds = [hp_inds, fp_inds, st_inds]
    vals = [hp_val, st_val, fp_val]

    for ind_ls, nv in zip(all_inds, vals):
        char_slot = get_slot_ls(file)[slot - 1]
        dat_slices = get_slot_slices(file)[slot - 1]
        for i in ind_ls:
            dat = (
                dat_slices[0]
                + char_slot[:i]
                + nv.to_bytes(2, "little")
                + char_slot[i + 2 :]
                + dat_slices[1]
            )

        with open(file, "wb") as f:
            f.write(dat)
    recalc_checksum(file)


def additem(file, slot, itemids, quantity):
    cs = get_slot_ls(file)[slot - 1]
    slices = get_slot_slices(file)
    s_start = slices[slot - 1][0]
    s_end = slices[slot - 1][1]

    with open(file, "rb") as f:
        dat = f.read()

        index = []
        cur = itemids
        if cur is None:
            return

        for ind, i in enumerate(cs):

            if (
                l_endian(cs[ind : ind + 1]) == cur[0]
                and l_endian(cs[ind + 1 : ind + 2]) == cur[1]
                and l_endian(cs[ind + 2 : ind + 3]) == 0
                and l_endian(cs[ind + 3 : ind + 4]) == 176
            ):
                index.append(ind + 4)
                # print(ind)

        if len(index) < 1:
            return None

        else:
            pos = index[0]

        with open(file, "wb") as fh:
            ch = (
                s_start
                + cs[:pos]
                + quantity.to_bytes(2, "little")
                + cs[pos + 2 :]
                + s_end
            )

            fh.write(ch)

        recalc_checksum(file)
        return True


def _get_stats(char_slot):
    # import_save()
    # names = get_charnames(r"C:/Users/James Zampa/AppData/Roaming/EldenRing/76561198059144503/ER0000.sl2")
    # print(names)
    #dict_stats = {}
    #for i, name in enumerate(names):
        # if name is None:
        #     continueC:\Users\James Zampa\AppData\Roaming\EldenRing\76561199402743988
    stats = get_stats(r"C:/Users/James Zampa/AppData/Roaming/EldenRing/76561199402743988/ER0000.sl2", char_slot)
        # if stats is None:
        #     continue
        # dict_stats[name] = stats[0]
        # # print(name)
        # # print(stats[0])
    return stats[0]


class EldenAgent:
    def __init__(self) -> None:
        self.keys_pressed = []
        self.keyboard = kb.Controller()
        self.path_elden_ring = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\ELDEN RING\\Game\\eldenring.exe'


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
elden_agent = EldenAgent()


def update_status(text):
    with open('status.txt', 'w') as f:
        f.write(text)


@app.route('/action/focus_window', methods=["POST"])
def focus_window():
    if request.method == 'POST':
        try:
            print('FOCUS WINDOW(Do Nothing)')
            try:
                #update_status('Focusing window')
                elden_agent.w = WindowMgr()
                elden_agent.w.find_window_wildcard('ELDEN RING.*')
                elden_agent.w.set_foreground()
            except Exception as e:
                print("ERROR: Could not fild Elden Ring Restarting")
                update_status('Could not fild Elden Ring restarting')
                time.sleep(60 * 3)
                os.system("taskkill /f /im eldenring.exe")
                time.sleep(60 * 5)
                subprocess.run([elden_agent.path_elden_ring])
                time.sleep(180)
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')

                press_q = True
                for i in range(15):
                    if press_q:
                        elden_agent.keyboard.press("q")
                        time.sleep(0.05)
                        elden_agent.keyboard.release("q")
                        press_q = False
                    else:
                        elden_agent.keyboard.press("e")
                        time.sleep(0.05)
                        elden_agent.keyboard.release("e")
                        press_q = True
                    time.sleep(1)
                time.sleep(30)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/load_save', methods=["POST"])
def load_save():
    if request.method == 'POST':
        try:
            print('LOAD SAVE')
            update_status('Loading save file')
            press_q = True
            for i in range(15):
                if press_q:
                    elden_agent.keyboard.press("q")
                    time.sleep(0.05)
                    elden_agent.keyboard.release("q")
                    press_q = False
                else:
                    elden_agent.keyboard.press("e")
                    time.sleep(0.05)
                    elden_agent.keyboard.release("e")
                    press_q = True
                time.sleep(1)
            time.sleep(30)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/death_reset', methods=["POST"])
def death_reset():
    if request.method == 'POST':
        try:
            elden_agent.keys_pressed = []
            print('DEATH RESET')
            update_status('Death reset')
            curr_reward = None
            curr_resets = None
            with open('obs_log.txt', 'r') as f:
                for line in f.readlines():
                    reward_match = re.search("Reward: (.+)", line)
                    if not reward_match is None:
                        curr_reward = float(reward_match[1])
                    resets_match = re.search("Num resets: (.+)", line)
                    if not resets_match is None:
                        curr_resets = int(resets_match[1])
            with open('obs_log.txt', 'w') as f:
                f.write(f"Dead: {True}")
                f.write("\n")
                f.write("FPS: {:.2f}".format(curr_reward))
                f.write("\n")
                f.write(f"Num resets: {curr_resets}")

            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


def press_key(key_to_press, duration):
    holding = False
    for key in elden_agent.keys_pressed:
        if type(key) != str and key[0] == key_to_press:
            key[1] += duration / 2
            holding = True
    
    if not holding:
        elden_agent.keyboard.press(key_to_press)
        elden_agent.keys_pressed.append([key_to_press, duration, time.time()])


@app.route('/action/custom/<action>', methods=["POST"])
def custom_action(action):
    if request.method == 'POST':
        try:
            print('CUSTOM ACTION')
            action = int(action)
            #update_status(f'Custom action: {action}')
            if action == 0:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.press('w')
                # self.keys_pressed.append('w')
            elif action == 1:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.press('s')
                # self.keys_pressed.append('s')
            elif action == 2:
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
                elden_agent.keyboard.press('a')
                # self.keys_pressed.append('a')
            elif action == 3:
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
                elden_agent.keyboard.press('d')
                # self.keys_pressed.append('d')
            elif action == 4:
                elden_agent.keyboard.release('w')
                elden_agent.keyboard.release('s')
                elden_agent.keyboard.release('a')
                elden_agent.keyboard.release('d')
            elif action == 5:
                press_key(kb.Key.space, 0.1)
            elif action == 6:
                press_key('4', 0.1)
            elif action == 7:
                press_key(kb.Key.shift_l, 0.1)
                press_key('4', 0.1)
            elif action == 8:
                press_key('5', 0.5)
            elif action == 9:
                press_key(kb.Key.shift_l, 0.1)
                press_key('5', 0.1)
            elif action == 10:
                press_key('r', 0.1)
            elif action == 11:
                press_key(kb.Key.space, 0.5)
            elif action == 12:
                press_key('f', 0.1)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/return_to_grace', methods=["POST"])
def return_to_grace():
    if request.method == 'POST':
        try:
            print('RETURN TO GRACE')
            update_status(f'Returning to grace')
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.release('s')
            elden_agent.keyboard.release('a')
            elden_agent.keyboard.release('d')

            time.sleep(1)

            elden_agent.keyboard.press('e')
            elden_agent.keyboard.press('3')
            time.sleep(0.1)
            elden_agent.keyboard.release('e')
            elden_agent.keyboard.release('3')

            time.sleep(1)

            elden_agent.keyboard.press(kb.Key.left)
            time.sleep(0.1)
            elden_agent.keyboard.release(kb.Key.left)

            time.sleep(1)

            elden_agent.keyboard.press('e')
            time.sleep(0.1)
            elden_agent.keyboard.release('e')

            time.sleep(11)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/lock_on', methods=["POST"])
def lock_on():
    if request.method == 'POST':
        try:
            #print('LOCK ON TOGGLE')
            #update_status(f'Locking on')
            #elden_agent.keyboard.press('q')
            #time.sleep(0.05)
            #elden_agent.keyboard.release('q')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/init_fight', methods=["POST"])
def init_fight():
    if request.method == 'POST':
        try:
            print('init fight')
            update_status(f'Initializing fight')
            elden_agent.keyboard.press('w')
            elden_agent.keyboard.press(kb.Key.space)
            time.sleep(2.35)
            elden_agent.keyboard.press('f')
            time.sleep(0.05)
            elden_agent.keyboard.release('f')
            time.sleep(4)
            #elden_agent.keyboard.release(kb.Key.space)
            #elden_agent.keyboard.release('w')

            elden_agent.keyboard.press('d')
            #elden_agent.keyboard.press(kb.Key.space)
            time.sleep(1)
            elden_agent.keyboard.release('d')
            #elden_agent.keyboard.press('w')
            time.sleep(2.5)
            #elden_agent.keyboard.release('w')

            #elden_agent.keyboard.press('w')
            elden_agent.keyboard.press('a')
            time.sleep(1)
            #elden_agent.keyboard.release('w')
            elden_agent.keyboard.release('a')

            #elden_agent.keyboard.press('w')
            time.sleep(1.5)
            elden_agent.keyboard.release('w')
            elden_agent.keyboard.release(kb.Key.space)
            
            elden_agent.keyboard.press('q')
            time.sleep(0.05)
            elden_agent.keyboard.release('q')

            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)



@app.route('/recording/start', methods=["POST"])
def start_recording():
    if request.method == 'POST':
        try:
            print('Start Recording')
            #update_status(f'Start recording')
            elden_agent.keyboard.press('=')
            time.sleep(0.05)
            elden_agent.keyboard.release('=')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/recording/stop', methods=["POST"])
def stop_recording():
    if request.method == 'POST':
        try:
            print('Stop Recording')
            #update_status(f'Stop recording')
            elden_agent.keyboard.press('-')
            time.sleep(0.05)
            elden_agent.keyboard.release('-')
            #time.sleep(0.05)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/recording/get_num_files', methods=["POST"])
def get_num_files():
    if request.method == 'POST':
        try:
            print('get_num_files')
            vod_dir = r"E:\\Documents\\EldenRingAI\\vods"
            return json.dumps({'num_files': len(os.listdir(vod_dir))})
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)



@app.route('/recording/get_parry', methods=["POST"])
def get_parry():
    if request.method == 'POST':
        try:
            print('get_parry')
            vod_dir = r"E:\\Documents\\EldenRingAI\\vods"
            frames = b''
            min_ts = None
            if len(os.listdir(vod_dir)) == 0:
                return Response(status=404)
            for file in os.listdir(vod_dir):
                file_name = file.split(".")[0]
                ts = time.mktime(datetime.datetime.strptime(file_name, "%Y-%m-%d %H-%M-%S").timetuple())
                if min_ts is None:
                    min_ts = ts
                    file_to_rename = file
                elif min_ts > ts:
                    min_ts = ts
                    file_to_rename = file
            
            try:
                source = os.path.join(vod_dir, file_to_rename)
                clip = mp.VideoFileClip(source)
                clip.audio.write_audiofile(r"tmp.wav", ffmpeg_params=["-ac", "1", "-ar", "16000"])
                with wave.open("tmp.wav") as fd:
                    params = fd.getparams()
                    frames = fd.readframes(16000*2)
                parry_sound_bytes = str(base64.b64encode(frames))
                os.remove(source)
                return json.dumps({'parry_sound_bytes':parry_sound_bytes})
            except Exception as e:
                print(str(e))
                return json.dumps({'error':str(e)})
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)

@app.route('/recording/tag_latest/<max_reward>/<iteration>', methods=["POST"])
def tag_file(max_reward=None, iteration=None):
    if request.method == 'POST':
        try:
            print('Renaming run')
            #update_status(f'Naming recorded run #{int(iteration)}')
            request_json = request.get_json(force=True)

            max_ts = None
            file_to_rename = None
            vod_dir = r"E:\\Documents\\EldenRingAI\\vods"
            saved_runs_dir = r"E:\\Documents\\EldenRingAI\\saved_runs"
            parries_dir = r"E:\\Documents\\EldenRingAI\\parries"

            for file in os.listdir(vod_dir):
                file_name = file.split(".")[0]
                ts = time.mktime(datetime.datetime.strptime(file_name, "%Y-%m-%d %H-%M-%S").timetuple())
                if max_ts is None:
                    max_ts = ts
                    file_to_rename = file
                elif max_ts < ts:
                    max_ts = ts
                    file_to_rename = file
            
            source = os.path.join(vod_dir, file_to_rename)
            dest = os.path.join(saved_runs_dir, str(iteration) + "_" + str(max_reward) + '.mkv')
            shutil.move(source, dest)

            clip = mp.VideoFileClip(dest)
            clip.audio.write_audiofile(r"tmp.wav", ffmpeg_params=["-ac", "1", "-ar", "16000"])
            audio = AudioSegment.from_file(r"tmp.wav", format="wav")
            for i, parry in enumerate(request_json['parries']):
                combined = AudioSegment.empty()
                extract = audio[parry * 1000:(parry + 2) * 1000]
                combined += extract
                combined.export(os.path.join(parries_dir, str(iteration) + "_" + str(max_reward) + "_" + str(i).zfill(6) + ".wav"), format="wav")
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/stop_elden_ring', methods=["POST"])
def stop_elden_ring():
    if request.method == 'POST':
        try:
            print('STOP ELDEN RING')
            update_status(f'Stop Elden Ring')
            os.system("taskkill /f /im eldenring.exe")
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/start_elden_ring', methods=["POST"])
def start_elden_ring():
    if request.method == 'POST':
        try:
            print('START ELDEN RING')
            update_status(f'Start Elden Ring')
            
            subprocess.run([elden_agent.path_elden_ring])
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/action/release_keys', methods=["POST"])
def release_keys():
    if request.method == 'POST':
        try:
            print('RELEASE KEYS')
            #update_status(f'Release keys')
            
            for key in elden_agent.keys_pressed:
                if type(key) == str:
                    elden_agent.keyboard.release(key)
                    elden_agent.keys_pressed.remove(key)
                else:
                    if time.time() - key[2] > key[1]:
                        elden_agent.keyboard.release(key[0])
                        elden_agent.keys_pressed.remove(key)
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/status/update', methods=["POST"])
def status_update():
    if request.method == 'POST':
        try:
            request_json = request.get_json(force=True)
            update_status(f'{request_json["text"]}')
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)


@app.route('/obs/log', methods=["POST"])
def log_to_obs():
    if request.method == 'POST':
        try:
            print('Log to OBS')
            request_json = request.get_json(force=True)
            with open('obs_log.txt', 'w') as f:
                #f.write(f"Dead: {request_json['death']}")
                #f.write("\n")
                #f.write("FPS: {:.2f}".format(float(request_json['reward'])))
                #f.write("\n")
                f.write(f"Num resets: {request_json['num_run']}")
            with open('lowest_boss_hp.txt', 'w') as f:
                f.write(f"{float(request_json['lowest_boss_hp'])}")
            return Response(status=200)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)



@app.route('/stats/<char_slot>', methods=["GET"])
def request_stats(char_slot=None):
    if char_slot is None:
        return Response(status=400)
    
    if request.method == 'GET':
        try:
            print('GET STATS')
            stats = _get_stats(int(char_slot))
            json_stats = {'vigor' : stats[0],
                        'mind' : stats[1],
                        'endurance' : stats[2],
                        'strength' : stats[3],
                        'dexterity' : stats[4],
                        'intelligence' : stats[5],
                        'faith' : stats[6],
                        'arcane' : stats[7]}
            return json.dumps(json_stats)
        except Exception as e:
            return json.dumps({'error':str(e)})
    else:
        return Response(status=400)