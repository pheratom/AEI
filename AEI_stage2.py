# Arch Encrypted Install v 1.0 stage 2
import os

print('WARNING THE SCRIPT IS STILL UNDER DEVELOPMENT. DO NOT USE IT!')
print("Enter your account password to get su privileges.")
print("It will just give superuser privileges for your user terminal. It will save your time (~5 seconds) in future.")
os.system('sudo echo > /dev/null')
os.system('clear')
try:
    import colorama
    from colorama import Fore, Back, Style
except ModuleNotFoundError:
    os.system('sudo pacman -S --noconfirm python-pip')
    os.system('python3 -m pip install colorama')
finally:
    import colorama
    from colorama import Fore, Back, Style

while True:
    city = input('Enter your timezone city: ')
    os.system(f'timedatectl list-timezones | grep {city}')
    print('If the required time zone is not here, then after the next question, select "Are you sure? (y/n) n"')
    systemd_timezone_name = input('Enter your timezone name (exactly the same as in the output): ')
    answer = input('Are you sure? (y/n) ')
    if answer == 'n':
        continue
    os.system(f'ln -sf /usr/share/zoneinfo/{systemd_timezone_name} /etc/localtime')
    os.system(f'hwclock --systohc')


os.system('echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen')
os.system('echo LANG=en_US.UTF-8 >> /etc/locale.conf')
os.system('echo "127.0.0.1      localhost" >> /etc/hosts')
os.system('echo "::1              localhost" >> /etc/hosts')
os.system('echo "127.0.1.1    arch.localdomain arch" >> /etc/hosts')

print('Enter root password.')
os.system('passwd')

os.system('pacman -S --noconfirm grub efibootmgr networkmanager network-manager-applet dialog os-prober mtools dosfstools base-devel linux-lts-headers git ntfs-3g xdg-utils xdg-user-dirs')
os.system('cd /root')
os.system("cat /etc/mkinitcpio.conf | grep 'modconf' > hooks.txt")
with open('hooks.txt') as file:
    hooks = file.read()
    hooks = hooks[7:]
    hooks = hooks[:-2]
hooks = hooks.split()
block_id = hooks.index('block')
hooks.insert(block_id+1, 'encrypt')
hooks = ' '.join(hooks)
os.system("sed '/HOOKS=(/d' /etc/mkinitcpio.conf > /etc/mkinitcpio.tmp && rm /etc/mkinitcpio.conf && mv /etc/mkinitcpio.tmp /etc/mkinitcpio.conf")
os.system(f"echo 'HOOKS=({hooks})' >> /etc/mkinitcpio.conf")
os.system('mkinitcpio -p linux-lts')

os.system('grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id="ArchLinux Boot Manager"')
os.system('echo \'GRUB_GFXMODE="1920x1080,auto"\' >> /etc/default/grub')
os.system('echo \'GRUB_GFXPAYLOAD_LINUX="1920x1080"\' >> /etc/default/grub')
os.system('echo \'GRUB_DISABLE_OS_PROBER="false"\' >> /etc/default/grub')
os.system("sed '/GRUB_GFXMODE=/d' /etc/default/grub > /etc/default/tmp.txt && rm /etc/default/grub && mv /etc/default/tmp.txt /etc/default/grub && sed '/GRUB_GFXPAYLOAD_LINUX=/d' /etc/default/grub > /etc/default/tmp.txt && rm /etc/default/grub && mv /etc/default/tmp.txt /etc/default/grub && sed '/GRUB_CMDLINE_LINUX=/d' /etc/default/grub > /etc/default/tmp.txt && rm /etc/default/grub && mv /etc/default/tmp.txt /etc/default/grub")

with open('luks.txt') as file:
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
os.system(f'echo \'GRUB_CMDLINE_LINUX="cryptdevice=UUID={blkid}:{luks_short}:allow-discards root=/dev/mapper/{luks_short}"\' >> /etc/default/grub')

os.system('grub-mkconfig -o /boot/grub/grub.cfg')
os.system('systemctl enable NetworkManager')

username = input('Enter username: ')
os.system(f'useradd -mG wheel {username}')
os.system('echo \'%wheel ALL=(ALL) ALL\' >> /etc/sudoers')
print('Arch Linux installed! Please reboot')
os.system('exit')