import ctypes

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT_RESERVE = 0x3000
PAGE_READWRITE = 0x04
MEM_RELEASE = 0x8000

def inject_dll(pid, dll_path):
    kernel32 = ctypes.windll.kernel32Ye

    process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not process:
        print(f"  Не удалось открыть процесс с PID {pid}")
        return

    dll_bytes = dll_path.encode('utf-16le')
    address = kernel32.VirtualAllocEx(process, 0, len(dll_bytes), MEM_COMMIT_RESERVE, PAGE_READWRITE)
    if not address:
        kernel32.CloseHandle(process)
        return

    written = ctypes.c_ulong(0)
    if not kernel32.WriteProcessMemory(process, address, dll_bytes, len(dll_bytes), ctypes.byref(written)):
        kernel32.VirtualFreeEx(process, address, 0, MEM_RELEASE)
        kernel32.CloseHandle(process)
        return

    thread = kernel32.CreateRemoteThread(process, 0, 0, kernel32.LoadLibraryW, address, 0, 0)
    if not thread:
        kernel32.VirtualFreeEx(process, address, 0, MEM_RELEASE)
        kernel32.CloseHandle(process)
        return

    kernel32.WaitForSingleObject(thread, -1)
    kernel32.CloseHandle(thread)
    kernel32.VirtualFreeEx(process, address, 0, MEM_RELEASE)
    kernel32.CloseHandle(process)

if __name__ == "__main__":
    pid = int(input("Введите PID процесса: "))
    dll_path = input("Введите путь к DLL: ")
    inject_dll(pid, dll_path)
