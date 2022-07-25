# Arch Encrypted Install v 1.0
import os
import sys
import time
import colorama
from colorama import Fore, Back, Style
from AEI_functions import PreCheck
from AEI_functions import Install
from AEI_functions import check_uefi
colorama.init(autoreset = True)

def warning():
    print('{Fore.RED}{Style.BRIGHT}WARNING THE SCRIPT IS STILL UNDER DEVELOPMENT. DO NOT USE IT!')
    time.sleep(4)
    os.system('clear')

def welcome_stage0():
    #Displays warning that script is still under development
    warning()
    print("""{Fore.GREEN}
                   ______ _____        __   ___  
             /\   |  ____|_   _|      /_ | / _ \ 
            /  \  | |__    | |   __   _| || | | |
           / /\ \ |  __|   | |   \ \ / / || | | |
          / ____ \| |____ _| |_   \ V /| || |_| |
         /_/    \_\______|_____|   \_/ |_(_)___/ """)  # https://www.fontchanger.net/ascii-text.html Font - Big
    print(f"{Fore.RED}{Style.BRIGHT}Warning! This script supports UEFI devices only!")
    check_uefi()
    #Shows menu where you can choose device partitions
    PreCheck()
    Install.stage1()

if __name__ == '__main__':
    if 'stage2' in sys.argv:
        Install.stage2()
    else:
        welcome_stage0()
