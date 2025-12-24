# setup.py
import os
import subprocess

def setup_repo():
    if not os.path.exists('.git'):
        print("📁 Инициализация Git...")
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'branch', '-M', 'main'])
        remote = input("🌐 Введите ссылку на GitHub (https://github.com/user/repo.git): ")
        subprocess.run(['git', 'remote', 'add', 'origin', remote])

    print("✅ Настройка GitHub Actions...")
    os.makedirs('.github/workflows', exist_ok=True)
    with open('.github/workflows/deploy.yml', 'w') as f:
        f.write('''name: Deploy to Production
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sync to VPS
        uses: appleboy/scp-action@v0.1.5
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_KEY }}
          source: "*,.env"
          target: "/var/www/nightmonopoly"
''')
    print("✅ .github/workflows/deploy.yml создан")
    print("📌 Добавь VPS_HOST, VPS_USER, VPS_KEY в Settings → Secrets на GitHub")

if __name__ == '__main__':
    setup_repo()