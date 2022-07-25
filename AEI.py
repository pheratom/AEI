# Arch Encrypted Install v 1.0 stage 1
import os
import sys
import time
print('WARNING THE SCRIPT IS STILL UNDER DEVELOPMENT. DO NOT USE IT!')
time.sleep(4)
os.system('clear')
import colorama
from colorama import Fore, Back, Style
colorama.init(autoreset = True)
print("""
           ______ _____        __   ___  
     /\   |  ____|_   _|      /_ | / _ \ 
    /  \  | |__    | |   __   _| || | | |
   / /\ \ |  __|   | |   \ \ / / || | | |
  / ____ \| |____ _| |_   \ V /| || |_| |
 /_/    \_\______|_____|   \_/ |_(_)___/ """)

# Check UEFI support.
print(f"{Fore.RED}{Style.BRIGHT}Warning! This script supports UEFI devices only!")
os.system("[ -d /sys/firmware/efi ] && echo \"UEFI\" > uefi_status.txt || echo \"Legacy\" > uefi_status.txt")
with open('uefi_status.txt', 'r') as file:
    file_contents = file.read()
    if 'UEFI' in file_contents:
        print(f"{Fore.GREEN}{Style.BRIGHT}Your PC supports UEFI.")
        os.system('rm uefi_status.txt')
    elif 'Legacy' in file_contents:
        print(f"{Fore.RED}{Style.BRIGHT}Oops. Your PC don't support UEFI.")
        os.system('rm uefi_status.txt')
        sys.exit()
    else:
        print("Unknown Error!")
        os.system('rm uefi_status.txt')
        sys.exit()

os.system('lsblk')
efi_partition = input("Enter EFI (ESP) partition (example /dev/sda1): ")
answer = input('Are you sure? (y/n) ')
if answer == 'y':
    pass
elif answer == 'n':
    print('Exitting.')
    sys.exit()

os.system('lsblk')
luks_cryptdata_partition = input("Enter partition for LUKS (example /dev/sda4): ")
answer = input('Are you sure? (y/n) ')
if answer == 'y':
    pass
elif answer == 'n':
    print('Exitting.')
    sys.exit()

# Start installation process.

answer = input(f'Format EFI (ESP) partition ({efi_partition}) (y/n)? ')
if answer == 'y':
    os.system(f'sudo mkfs.fat -F32 {efi_partition}')
elif answer == 'n':
    print(f'OK. {efi_partition} will not be formatted.')
else:
    print('Error. Exitting')
    sys.exit()

answer = input(f"Do you have an AMD or Intel processor? (amd/intel): ")
if answer == 'amd':
    processor = 'amd'
elif answer == 'intel':
    processor = 'intel'
else:
    print('Error! Exitting')
    sys.exit()

luks_short = luks_cryptdata_partition[5:]
luks_short = luks_short + '_crypt'
os.system(f'sudo cryptsetup -y -v luksFormat {luks_cryptdata_partition}')
os.system(f'sudo cryptsetup open {luks_cryptdata_partition} {luks_short}')

os.system(f'sudo mkfs.ext4 /dev/mapper/{luks_short}')
os.system(f'sudo mount /dev/mapper/{luks_short} /mnt')
os.system(f'sudo mkdir /mnt/boot')
os.system(f'sudo mount {efi_partition} /mnt/boot')

os.system(f"sudo pacstrap /mnt base linux-lts linux-firmware vim nano {processor}-ucode python3 python-pip")
os.system('sudo genfstab -U /mnt >> /mnt/etc/fstab')

os.system('sudo cp AEI_stage2.py /mnt/root')
os.system(f'echo "{luks_cryptdata_partition}" > luks.txt')
os.system('sudo cp luks.txt /mnt/root')
os.system('sudo arch-chroot /mnt python3 /root/AEI_stage2.py')
