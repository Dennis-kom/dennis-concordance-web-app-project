#!/usr/bin/env python
path = r'C:\repositories\dennis-concordance-web-app-project\requierments.txt'
content = """blinker==1.9.0
cffi==2.0.0
click==8.3.1
colorama==0.4.6
cryptography==46.0.4
Flask==3.1.2
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.3
oracledb==3.4.2
pycparser==3.0
typing_extensions==4.15.0
Werkzeug==3.1.5
"""
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"File created successfully at {path}")
with open(path, 'r') as f:
    lines = f.readlines()
    print(f"Content ({len(lines)} lines):")
    f.seek(0)
    print(f.read())

