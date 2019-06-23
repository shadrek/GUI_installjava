#!/usr/bin/env python
import platform
import distro
import glob
import shutil
import os
import tarfile
import stat
import subprocess
import tkinter
import tkinter.messagebox


def check_linux():
    islinux = platform.system()
    if islinux == "Linux" or islinux == "Linux2" or islinux == "GNU" or islinux == "GNU/*":
        return islinux
    else:
        tkinter.messagebox.showwarning(
            "Failed Test", "your system is not linux - this script only works on arch based linux systems. Sorry, bye...")
        exit()


def check_distro(islinux):
    thisDistro = distro.id()
    if thisDistro != "manjaro" and thisDistro != "arch" and thisDistro != "antergos":
        tkinter.messagebox.showwarning(
            "Failed Test", f"your {islinux} system is {thisDistro} - this script only works on Arch based systems. Sorry, bye...")
        exit()


def check_root():
    if os.geteuid() != 0:
        tkinter.messagebox.showerror(
            "Error", "This script must be run as root. (Hint: use sudo)")
        exit()


def run_choice():
    choice = tkinter.messagebox.askyesno(
        "Oracle Java Will Be Installed", "Do you wish to install Oracle Java on this system?")

    if choice is not True:
        print("bye...")
        exit()


def get_jdk_version():
    jdkfilesB_List = glob.glob('jdk*.tar.gz', recursive=False)
    numOfFiles = len(jdkfilesB_List)

    if numOfFiles > 1:
        tkinter.messagebox.showerror(
            "ERROR", f"you have {numOfFiles} files starting with 'jdk' in the same folder with this script. Delete or move the excess files and leave only the correct downloaded jdk*.tar.gz in the folder")
        exit()
    elif numOfFiles == 0:
        tkinter.messagebox.showerror(
            "ERROR", "No downloaded jdk*.tar.gz file in the folder with this script. Please place your downloaded jdk*.tar.gz into the same folder with this script and run the script again.")
        exit()

    jdkTarFile = jdkfilesB_List[0]
    return jdkTarFile


def untar_jdk(jdk):
    print("Uncompressing the jdk tarfile")

    if jdk.endswith("tar.gz"):
        tar = tarfile.open(jdk, "r:gz")
        tar.extractall()
        tar.close()
    elif jdk.endswith("tar"):
        tar = tarfile.open(jdk, "r:")
        tar.extractall()
        tar.close()

    oneDirup = '../'

    # TrashDir = ("/home/$SUDO_USER/.local/share/Trash/files")

    # if (os.path.isdir(TrashDir)):
    #     if os.path.isfile(TrashDir) or os.path.islink(TrashDir):
    #         os.unlink(TrashDir)
    #         print(TrashDir, "was a link or file so unlinked it")
    #     shutil.move(jdk, TrashDir)
    #     print("Moved your", jdk, "Folder to the rubbish bin")
    # else:
    shutil.move(jdk, oneDirup)


def move_jdk():
    # Check if java directory exists - if so check if same jdk version directory
    # already exists in the java directory. If so delete it first, then move unpacked
    # directory there. If java directory does not exist, create it first then  move
    # the unpacked directory there.
    jvm_Dir = "/usr/lib/jvm/"
    upkdJDKlist = glob.glob('jdk*.*.*', recursive=False)
    numOfFiles = len(upkdJDKlist)
    if numOfFiles > 1:
        tkinter.messagebox.showerror(
            "ERROR", f"There are {numOfFiles} files or folders with names starting with the letters 'jdk'. You must manually remove the wrong folders and try and run the script again.")
        exit()
    elif numOfFiles == 0:
        tkinter.messagebox.showerror(
            "ERROR", "Something went wrong - there is no suitable uncompressed jdk folder in the folder with this script")
        exit()
    upkdJDK = upkdJDKlist[0]
    combinedDir = os.path.join(jvm_Dir, upkdJDK)

    if os.path.exists(jvm_Dir):
        print(jvm_Dir, "exists")
        if os.path.exists(combinedDir):
            print(upkdJDK, "exists already")
            if os.path.isfile(combinedDir) or os.path.islink(combinedDir):
                os.unlink(combinedDir)
                print(combinedDir, "was a file or link.. unlinked it")
            else:
                shutil.rmtree(combinedDir)
                print(upkdJDK, "deleted to enable re-installation")
        else:
            print(combinedDir, "not found, which is good")
    else:
        try:
            os.mkdir(jvm_Dir)
        except OSError:
            tkinter.messagebox.showerror(
                "ERROR", f"Creation of {jvm_Dir} failed")
        else:
            tkinter.messagebox.showinfo(
                "INFO", f"Successfully created the directory {jvm_Dir}")

    shutil.move(upkdJDK, jvm_Dir)
    print("Moved the new", upkdJDK, " to ", jvm_Dir)
    return upkdJDK, combinedDir


def install_path(jdkVerDir):
    pathDir = "/etc/profile"
    oldDir = ".java.old"
    ext2 = "2"
    pathDirOld = pathDir + oldDir
    pathDir2nd = pathDir + ext2
    print(pathDirOld, " is pathDirOld")
    print(pathDir2nd, " is pathDir2nd")
    print("Installing the java paths into", pathDir)

    if os.path.exists(pathDir):
        if os.path.isfile(pathDirOld):
            os.remove(pathDirOld)
            print("Deleted", pathDirOld)

        shutil.copyfile(pathDir, pathDirOld)

    if os.path.isfile(pathDir2nd):
        os.remove(pathDir2nd)

    old_paths = ['JAVA', 'JAVA_HOME', 'JRE_HOME', 'export PATH']

    with open(pathDir) as oldfile, open(pathDir2nd, 'w') as newfile:
        for line in oldfile:
            if not any(old_path in line for old_path in old_paths):
                newfile.write(line)

    spc = "\n"
    JAVA = "JAVA_HOME=" + jdkVerDir + "\n"
    JRE = "JRE_HOME=$JAVA_HOME/jre\n"
    #  PATH1 = "PATH=$PATH:$JAVA_HOME/bin:$JRE_HOME/bin\n"
    ex1 = "export JAVA_HOME\n"
    ex2 = "export JRE_HOME\n"
    # ex3 = "export PATH"

    fulljavaPath = spc + JAVA + JRE + ex1 + ex2
    print(fulljavaPath, "is what's entered into the path file")

    with open(pathDir2nd, 'a') as myfile:
        myfile.write(fulljavaPath)

    print("full path written")

    os.remove(pathDir)
    os.rename(pathDir2nd, pathDir)
    print("Java paths now installed in your", pathDir)


def make_executable():
    # check if file is executable. If not make it so.
    filepathList = ['/usr/bin/java', '/usr/bin/javac',
                    '/usr/bin/javap', '/usr/bin/javadoc']

    for file in filepathList:
        st = os.stat(file)
        isitExe = bool(st.st_mode & stat.S_IXUSR)
        if not isitExe:
            print(file, " is not executable, so making it so:")
            os.chmod(file, st.st_mode | stat.S_IEXEC)
        else:
            print(file, "is already executable")


def set_arch_java(jdkver, jdkVerDir):

    if os.path.isfile("./local_archlinux-java"):
        print("Using local_archlinux-java helper script to set java environment")
        subprocess.run(["./local_archlinux-java", "set", jdkver])
    elif os.path.isfile("/usr/bin/archlinux-java"):
        print("Found archlinux-java helper script so using it to set java environment")
        subprocess.run(["./local_archlinux-java", "set", jdkver])
    else:
        src1 = os.path.join(jdkVerDir, 'bin/java')
        dest1 = '/usr/bin/java'

        src2 = os.path.join(jdkVerDir, 'bin/javac')
        dest2 = '/usr/bin/javac'

        src3 = os.path.join(jdkVerDir, 'bin/javadoc')
        dest3 = '/usr/bin/javadoc'

        src4 = os.path.join(jdkVerDir, 'bin/javap')
        dest4 = '/usr/bin/javap'

        if os.path.islink('/usr/bin/java'):
            os.unlink('/usr/bin/java')

        if os.path.islink('/usr/bin/javac'):
            os.unlink('/usr/bin/javac')

        if os.path.islink('/usr/bin/javadoc'):
            os.unlink('/usr/bin/javadoc')

        if os.path.islink('/usr/bin/javap'):
            os.unlink('/usr/bin/javap')

        os.symlink(src1, dest1)
        os.symlink(src2, dest2)
        os.symlink(src3, dest3)
        os.symlink(src4, dest4)

        install_path(jdkVerDir)
        print("No archlinux-java script found, so manually symlinked everything")
        make_executable()


def bye(upkdJDKver):
    tkinter.messagebox.showinfo(
        "Info", f"Java {upkdJDKver} now fully installed on this computer.\n You can test which java by entering 'java -version at the terminal prompt. bye...")


def main():
    islinux = check_linux()
    check_distro(islinux)
    check_root()
    run_choice()
    jdkTarName = get_jdk_version()
    untar_jdk(jdkTarName)
    upkdJDKver, jdkVerDir = move_jdk()
    set_arch_java(upkdJDKver, jdkVerDir)
    bye(upkdJDKver)


if __name__ == '__main__':
    main()
