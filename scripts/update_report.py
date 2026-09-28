"""Run the analyses and replace only the README's generated output block."""

from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    readme = root / 'README.md'
    content = readme.read_text()
    start = content.index('```bash\n', content.index('**Output**:')) + len('```bash\n')
    end = content.index('```', start)
    output = []
    for script in ('payback.py', 'payback_evening_only.py',
                   'payback_evening_morning_optional.py', 'payback_intraday.py'):
        command = f'venv/bin/python {script}'
        print(command, flush=True)
        result = subprocess.run([sys.executable, script], cwd=root, text=True,
                                stdout=subprocess.PIPE, check=True)
        print(result.stdout, end='', flush=True)
        output.append(command + '\n' + result.stdout.rstrip() + '\n')
    temporary = readme.with_suffix('.md.tmp')
    temporary.write_text(content[:start] + '\n\n'.join(output) + content[end:])
    temporary.replace(readme)


if __name__ == '__main__':
    main()
