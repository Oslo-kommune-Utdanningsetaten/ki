# KI for Osloskolen

Students and teachers need access to LLM chatbots, but current commercial providers do not offer the personal security nor the granular control of student access which is needed in school. The ki.osloskolen.no web app solves this problem by:

- Wrapping all chatbot conversations behind a single API key, making it impossible for the LLM provider to match conversation data with user ID
- Not storing any user or conversation data on the backend
- Allowing teachers to create and grant time-limited access to bots for specific Feide groups (e.g. teaching groups)

This repo contains the complete code for the ki.osloskolen.no web app. If you'd like to set this up for your school or county, here's barebones guide to get this whole thing up and running. Technical knowledge is required.

## Which technology is involved?

- Database: MariaDB
- Backend: Python and Django
- Frontend: Vue, JavaScript, CSS
- Authentication: Oauth via Feide

## Up and running, as developer

- You need docker and docker-compose, python v3.13, poetry (`pip install poetry`) and node.js (v18+) installed on your system and available from the command line
- `git clone` this repo
- Make copies of these files, and modify the variables to match your configuration
  - `.env-example` --> `.env`
  - `frontend/.env-example` --> `frontend/.env`
  - `backend/.env-example` --> `backend/.env`
- Note that in addition to database credentials, the environment expects Azure and Feide specifics
- Containerized running of the database and adminer (for UI access to the DB): `docker-compose up --build` (refer to `compose.yml` and `.env` files)
- Install everything the server/backend needs: `cd backend && poetry install`
- Run migrations to get all database tables set up correctly `python manage.py makemigrations`
- Start the backend with `python manage.py runserver 5000`
  - Can also be started from a poetry shell with `poe run-server`
- Install everything the frontend needs: `cd frontend && npm install`
- Start the frontend with `npm run dev` and point your browser at http://localhost:5173
- You should now redirected to Feide for authentication
- There's probably no way that actually worked on the first try :)
- Hopefully, you know enough to debug your way out of any problems. If not, feel free to contact the maintainers for advice <3

### MacOS tips

- On your mac, go into settings and turn off AirPlay receiver, because this also runs on port 5000 (same as the backend). Or fiddle around with port config on the server to use a different port.
- Make sure you have Homebrew installed
- For node.js, use [Node Version Manager (nvm)](https://github.com/nvm-sh/nvm) or install with `brew install node`
- Homebrew some more:

```
brew install python@3.13
brew install poetry
brew install --cask docker
brew install pkg-config
brew install openssl
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl/lib/pkgconfig"
```

Consider putting those last three lines in your .bashrc or equivalent, to always have a working OpenSSL on your system.

## Contributing

PRs very welcome 🙌

1. Fork the repo
2. Make changes
3. Run tests
4. Create a PR, with a proper explanation of what the change does and why it should be included

## License

See [License](LICENSE.md)
