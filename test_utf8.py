import sys
import locale
import os

print(f"Python default encoding: {sys.getdefaultencoding()}")
print(f"Locale encoding: {locale.getpreferredencoding()}")
print(f"Stdout encoding: {sys.stdout.encoding}")
print(f"File encoding (test): ", end="")

# Write a test file
with open('test_utf8.txt', 'w', encoding='utf-8') as f:
    f.write('可回收\n')
    f.write('22号楼南侧\n')

# Read it back
with open('test_utf8.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    print(f"Read back: {content!r}")

os.remove('test_utf8.txt')
