import os
import sys
import colorama
from colorama import Fore, Style, Back
colorama.init(autoreset=True)

def check_uefi():
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

class PreCheck:
    def __init__(self):
        pass

    def precheck(self):
        os.system('lsblk')
        global efi_partition
        efi_partition = input("Enter EFI (ESP) partition (example /dev/sda1): ")
        answer = input('Are you sure? (y/n) ')
        if answer == 'y':
            pass
        elif answer == 'n':
            print('Exitting.')
            sys.exit()

        os.system('lsblk')
        global luks_cryptdata_partition
        luks_cryptdata_partition = input("Enter partition for LUKS (example /dev/sda4): ")
        answer = input('Are you sure? (y/n) ')
        if answer == 'y':
            pass
        elif answer == 'n':
            print('Exitting.')
            sys.exit()

        answer = input(f'Format EFI (ESP) partition ({efi_partition}) (y/n)? ')
        if answer == 'y':
            os.system(f'sudo mkfs.fat -F32 {efi_partition}')
        elif answer == 'n':
            print(f'OK. {efi_partition} will not be formatted.')
        else:
            print('Error. Exitting')
            sys.exit()

        answer = input(f"Do you have an AMD or Intel processor? (amd/intel): ")
        global processor
        if answer == 'amd':
            processor = 'amd'
        elif answer == 'intel':
            processor = 'intel'
        else:
            print('Error! Exitting')
            sys.exit()

class Install:
    def __init__(self):
        pass
    def stage1(self):
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

        os.system('sudo cp AEI* /mnt/root')
        os.system(f'echo "{luks_cryptdata_partition}" > luks.txt')
        os.system('sudo cp luks.txt /mnt/root')
        os.system('sudo arch-chroot /mnt python3 /root/AEI.py stage2')

    def stage2(self):
        print('{Fore.RED}{Style.BRIGHT}WARNING THE SCRIPT IS STILL UNDER DEVELOPMENT. DO NOT USE IT!')
        while True:
            city = input('Enter your timezone city: ')
            os.system(f'timedatectl list-timezones | grep {city}')
            print('If the required time zone is not here, then after the next question, select "Are you sure? (y/n) n"')
            systemd_timezone_name = input('Enter your timezone name (exactly the same as in the output): ')
            answer = input('Are you sure? (y/n) ')
            if answer == 'n':
                continue
            elif answer == 'y':
                break

        os.system(f'ln -sf /usr/share/zoneinfo/{systemd_timezone_name} /etc/localtime')
        os.system(f'hwclock --systohc')

        os.system('echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen')
        os.system('echo LANG=en_US.UTF-8 >> /etc/locale.conf')
        os.system('echo "127.0.0.1      localhost" >> /etc/hosts')
        os.system('echo "::1              localhost" >> /etc/hosts')
        os.system('echo "127.0.1.1    arch.localdomain arch" >> /etc/hosts')

        print('Enter root password.')
        os.system('passwd')

        os.system(
            'pacman -S --noconfirm grub efibootmgr networkmanager network-manager-applet dialog os-prober mtools dosfstools base-devel linux-lts-headers git ntfs-3g xdg-utils xdg-user-dirs')
        os.system('cd /root')
        os.system("cat /etc/mkinitcpio.conf | grep 'modconf' > hooks.txt")
        with open('hooks.txt') as file:
            hooks = file.read()
            hooks = hooks[7:]
            hooks = hooks[:-2]
        hooks = hooks.split()
        block_id = hooks.index('block')
        hooks.insert(block_id + 1, 'encrypt')
        hooks = ' '.join(hooks)
        os.system(
            "sed '/HOOKS=(/d' /etc/mkinitcpio.conf > /etc/mkinitcpio.tmp && rm /etc/mkinitcpio.conf && mv /etc/mkinitcpio.tmp /etc/mkinitcpio.conf")
        os.system(f"echo 'HOOKS=({hooks})' >> /etc/mkinitcpio.conf")
        os.system('mkinitcpio -p linux-lts')

        os.system('grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id="ArchLinux Boot Manager"')
        os.system('echo \'GRUB_GFXMODE="1920x1080,auto"\' >> /etc/default/grub')
        os.system('echo \'GRUB_GFXPAYLOAD_LINUX="1920x1080"\' >> /etc/default/grub')
        os.system('echo \'GRUB_DISABLE_OS_PROBER="false"\' >> /etc/default/grub')
        os.system(
            "sed '/GRUB_GFXMODE=/d' /etc/default/grub > /etc/default/tmp.txt && rm /etc/default/grub && mv /etc/default/tmp.txt /etc/default/grub && sed '/GRUB_GFXPAYLOAD_LINUX=/d' /etc/default/grub > /etc/default/tmp.txt && rm /etc/default/grub && mv /etc/default/tmp.txt /etc/default/grub && sed '/GRUB_CMDLINE_LINUX=/d' /etc/default/grub > /etc/default/tmp.txt && rm /etc/default/grub && mv /etc/default/tmp.txt /etc/default/grub")

        with open('/root/luks.txt') as file:
            luks_partition = file.read()
            luks_partition = luks_partition.rstrip()
        luks_short = luks_partition[5:]
        luks_short = luks_short + '_crypt'

        os.system(f'blkid {luks_partition} > blkid.txt')
        with open('blkid.txt') as file:
            blkid = file.read()
        blkid = blkid.split()
        for i in blkid:
            if not i.startswith('UUID'):
                blkid.remove(i)
        for i in blkid:
            if i.startswith('PARTUUID'):
                blkid.remove(i)
        blkid = ''.join(blkid)
        blkid = blkid[6:-1]
        os.system(
            f'echo \'GRUB_CMDLINE_LINUX="cryptdevice=UUID={blkid}:{luks_short}:allow-discards root=/dev/mapper/{luks_short}"\' >> /etc/default/grub')

        os.system('grub-mkconfig -o /boot/grub/grub.cfg')
        os.system('systemctl enable NetworkManager')

        username = input('Enter username: ')
        os.system(f'useradd -mG wheel {username}')
        print(f'Enter {username} password:')
        os.system(f'passwd {username}')
        os.system('echo \'%wheel ALL=(ALL) ALL\' >> /etc/sudoers')
        print(f'{Fore.GREEN}{Style.BRIGHT}{Back.LIGHTCYAN_EX}Arch Linux installed! Please reboot')
        os.system('exit')