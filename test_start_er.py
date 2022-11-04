import os
import time
import subprocess
import re


def launch_er():
    # The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    subprocess.Popen('./run_er.sh', stdout=subprocess.PIPE, 
                      shell=True, preexec_fn=os.setsid)


def get_er_process_ids():
    proc1 = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(['grep', 'start_protected_game.exe'], stdin=proc1.stdout,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    process_ids = []
    proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
    out, err = proc2.communicate()
    for line in str(out).split("james      "):
        match = re.search(r"(\d+)+.*", line)
        if not match is None:
            process_ids.append(match[1])
    return process_ids



def stop_er():
    for id in get_er_process_ids():
        subprocess.Popen(['kill', '-9', id], stdout=subprocess.PIPE)

def main():
    launch_er()
    time.sleep(60)
    stop_er()
    time.sleep(60)
    launch_er()
    time.sleep(60)
    stop_er()
    #print(get_pid('start_protected_game'))
    # Iterate over all running process


    
    #print(matches[2])
    #print('err: {0}'.format(err))

if __name__ == "__main__":
    main()
