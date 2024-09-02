# KI for Osloskolen

## Getting started, on a mac

- `git clone` this repo
- Make sure you have a `frontend/.env` and `backend/.env` with everything that's needed
- Make sure you have Homebrew installed
- Install node.js `brew install node` or use Node Version Manager (nvm) for better version control
- Homebrew some more:
```
brew install python@3.11
brew install poetry
brew install --cask docker
brew install mariadb
sudo mariadb-secure-installation
mysql.server start
```
- Instead of `mysql.server start` you could use `brew services start mariadb` if you want mariadb to run as a service, always on
- `cd frontend && npm install`
- Spin up the frontend `npm run dev` (should now be running on port http://localhost:5173)
- Go into settings, turn off AirPlay receiver, because this also runs on port 5000 (same as the backend)
- Connect to mysql and `create database ki;`
- Back in the terminal, set up the ki database: `mysql ki < ki.sql` (provided you're in posession of the ki.sql file)
- `cd backend && poetry shell`. This attemps to install all the associated python packages listed in pyproject.tom. This will likely give you various problems, here are some of the things you might have to do:
```
brew install pkg-config
brew install openssl
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl/lib/pkgconfig"
```

Eventually, run `python manage.py runserver 5000` to spin up the backend. At which point the frontend will have something to connect to 🙌

Also, if you're running uBlock in you browser, disable it for http://localhost:5173 in order to allow for Feide auth.


## Getting started, on a PC
TBA

