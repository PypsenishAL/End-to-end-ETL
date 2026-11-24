from pathlib import Path

ROOT = Path(__file__).resolve()
sql_dir = Path(r'D:\etl\project\sql')
sql_files = sorted([path for path in sql_dir.glob(pattern='*.sql')])
print(sql_files)