# Free CP

A small Persian Flask website with:
- G = first name, P = family name
- one spin per exact G+P combination every 24 hours
- admin page showing names, spin time, and result

## Run locally on a computer
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run: `python -m venv .venv`
4. Activate it:
   - Windows: `.venv\\Scripts\\activate`
   - macOS/Linux: `source .venv/bin/activate`
5. Run: `pip install -r requirements.txt`
6. Set admin values before starting:
   - Windows PowerShell:
     `$env:ADMIN_G="parsa"; $env:ADMIN_P="CHOOSE_A_STRONG_PASSWORD"; $env:SECRET_KEY="put-a-long-random-secret-here"`
   - macOS/Linux:
     `export ADMIN_G=parsa`
     `export ADMIN_P='CHOOSE_A_STRONG_PASSWORD'`
     `export SECRET_KEY='put-a-long-random-secret-here'`
7. Run: `python app.py`
8. Open `http://127.0.0.1:5000` on that computer.

Admin page: `/admin`

## Publish online (Render)
1. Create a GitHub account and a Render account.
2. Upload this project to a new GitHub repository.
3. In Render choose **New +** -> **Blueprint**, connect the repository, and let Render read `render.yaml`.
4. In Render's environment settings, set:
   - `ADMIN_G` = `parsa` (or change it)
   - `ADMIN_P` = a NEW strong admin password. Do not reuse a password from another account.
5. Ensure the service has the persistent disk configured at `/var/data` (the Blueprint requests it). SQLite data will be stored there.
6. Deploy. Render will provide a public `https://...onrender.com` address. Open it on your phone.
7. Admin login is at `https://YOUR-SITE/admin`.

Important:
- The admin credentials are server environment variables, not shown on the public page.
- G and P are names, not game-account passwords. The admin panel displays them.
- The 24-hour limit is attached to the exact pair of entered names. This is not identity verification: someone can bypass it by entering a different spelling/name. For a stronger limit, add phone/email verification or user accounts.
- The wheel's prize list is demo content. Configure real prizes and fulfill any reward manually; do not promise CP unless you can provide it.
- Render persistent disks may require a paid plan; check the current pricing before deploying. Free hosting may sleep or not retain SQLite data.
