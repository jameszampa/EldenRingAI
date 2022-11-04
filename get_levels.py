import os
import shutil
import hexedit
import lzma, datetime


def ext():
    return "ER0000.sl2"


def run_command(subprocess_command, optional_success_out="OK"):
    try:
        subprocess_command()
    except Exception as e:
        print(e)
    return ("Successfully completed operation", optional_success_out)


def get_charnames(file):
    """wrapper for hexedit.get_names"""
    out = hexedit.get_names(file)
    return out


def copy_file(src, dst):
    shutil.copy(src, dst)


def archive_file(file, name, metadata, names):
    name = name.replace(" ", "_")

    if not os.path.exists(file):  # If you try to load a save from listbox, and it tries to archive the file already present in the gamedir, but it doesn't exist, then skip
        return

    lzc = lzma.LZMACompressor()
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d__(%I.%M.%S)")
    name = f"{name}__{date}"
    os.makedirs(f"./data/archive/{name}")


    with open(file, "rb") as fhi, open(f"./data/archive/{name}/ER0000.xz", 'wb') as fho:
        pc = lzc.compress(fhi.read())
        fho.write(pc)
        fho.write(lzc.flush())

        names = [i for i in names if not i is None]
        formatted_names = ", ".join(names)
        meta = f"{metadata}\nCHARACTERS: {formatted_names}"

    meta_ls = [i for i in meta]
    try:
        x = meta.encode("ascii") # Will fail with UnicodeEncodeError if special characters exist
        with open(f"./data/archive/{name}/info.txt", 'w') as f:
            f.write(meta)
    except:
        for ind,i in enumerate(meta):
            try:
                x = i.encode("ascii")
                meta_ls[ind] = i
            except:
                meta_ls[ind] = '?'
        fixed_meta = ""
        for i in meta_ls:
            fixed_meta = fixed_meta + i

        with open(f"./data/archive/{name}/info.txt", 'w') as f:
            f.write(fixed_meta)


def import_save():
    """Opens file explorer to choose a save file to import, Then checks if the files steam ID matches users, and replaces it with users id"""
    savedir = "save_data/"

    if os.path.isdir(savedir) is False:
        os.makedirs(savedir)
    d = r"C:/Users/James Zampa/AppData/Roaming/EldenRing/76561199402743988/ER0000.sl2"
    names = get_charnames(d)
    for name in names:
        if name is None:
            continue
        archive_file(d, name, "ACTION: Imported", names)
        newdir = "{}{}/".format(savedir, name.replace(" ", "-"))
        cp_to_saves_cmd = lambda: copy_file(d, newdir)
        if os.path.isdir(newdir) is False:
            cmd_out = run_command(lambda: os.makedirs(newdir))

            if cmd_out[0] == "error":
                print("---ERROR #1----")
                return

            cmd_out = run_command(cp_to_saves_cmd)
            if cmd_out[0] == "error":
                return

            # file_id = hexedit.get_id(f"{newdir}/{ext()}")


def get_stats(char_slot):
    # import_save()
    # names = get_charnames(r"C:/Users/James Zampa/AppData/Roaming/EldenRing/76561198059144503/ER0000.sl2")
    # print(names)
    #dict_stats = {}
    #for i, name in enumerate(names):
        # if name is None:
        #     continueC:\Users\James Zampa\AppData\Roaming\EldenRing\76561199402743988
    stats = hexedit.get_stats(r"/home/james/.local/share/Steam/steamapps/compatdata/1245620/pfx/drive_c/users/steamuser/AppData/Roaming/EldenRing/76561199402743988/ER0000.sl2", char_slot)
        # if stats is None:
        #     continue
        # dict_stats[name] = stats[0]
        # # print(name)
        # # print(stats[0])
    return stats[0]

