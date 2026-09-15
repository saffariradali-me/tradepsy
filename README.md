# Tradepsy

A private trading journal. Everything you enter stays on this device — there is
no account, no sync and no server behind it.

---

## Two ways to run it

### 1. Just open the file

Double-click **`tradepsy.html`**. The whole app works: trades, routines,
reports, the calendar, contracts, capital, the app lock, backups. Nothing is
fetched from the internet at any point.

The one thing you cannot do this way is **install it as an app**. That is not a
limitation of Tradepsy — browsers refuse to install any page opened as a file,
because `file://` is not a secure origin. No page can work around it.

### 2. Run it from a local address (needed to install it)

Double-click the launcher for your platform:

| Platform | File |
| --- | --- |
| Windows | `Start Tradepsy (Windows).bat` |
| macOS | `Start Tradepsy (macOS).command` |

It starts a small server on your own machine and opens the app at
`http://localhost:8642/tradepsy.html`. Nothing is exposed to your network — the
server listens on the loopback interface only, and serves this folder and
nothing else. Close the window or press `Ctrl+C` to stop it.

Needs Python 3. macOS: `xcode-select --install`. Windows:
[python.org/downloads](https://www.python.org/downloads/), ticking **Add
python.exe to PATH** during setup.

If you would rather use your own static server, any will do:

```
npx serve .
python3 -m http.server 8642
```

---

## Installing it as an app

1. Start the app with a launcher (way 2 above).
2. Open **Settings → Security → Install app**.
3. Press **Install app**.

It then lives in your Start menu or Applications folder, opens in its own window
with its own icon, and has no address bar or tabs.

**Chrome and Edge**, on Windows and macOS, do this from the button.

If the button does not appear, the panel lists the three things the browser
checks — a secure address, the manifest, the service worker — and marks which
one is missing, so you can see what to fix rather than guess.

**Safari** has no API a page can call, so the button cannot do it for you.
Use **File → Add to Dock** on macOS, or **Share → Add to Home Screen** on
iPhone and iPad. Everything else about the app is identical.

### Does the installed app still need the server running?

No. A service worker caches the whole app the first time it loads, so the
installed app opens with the server stopped and with no network at all. This is
tested: the app boots normally with the server process killed outright.

Leave the folder where it is. Deleting `sw.js`, `manifest.webmanifest` or
`icons/` breaks installing (though `tradepsy.html` alone still runs fine on its
own).

---

## ⚠️ Moving your journal between the two ways of running it

**A browser files saved data under the address it came from.** `file://…` and
`http://localhost:8642` are two different addresses, so they get two separate
journals. Open the app the other way and it will look empty — nothing is lost,
it is just filed under the other address.

To carry your journal across:

1. In the version that has your data: **Settings → Data & storage → Export data**.
2. Open the app the other way.
3. **Settings → Data & storage → Import data**, and pick the file you exported.

For the same reason, **keep the port at 8642**. `--port 8643` is a different
address and therefore a different, empty journal. If the port is genuinely busy
the launcher stops and says so rather than quietly moving — that refusal is
protecting your data.

You can also open `http://localhost:8642/` on its own; the launcher serves the
app there too.

---

## The trading day

The journal day runs **03:00 Tehran to 03:00 Tehran**, and is not configurable.
A session that ends at two in the morning belongs to the day it started on.

At 03:00 Tehran the routines reset, the start and end of day reports clear, the
daily drawdown limit goes back to zero and the calendar moves on. Nothing is
deleted — the day that just closed keeps its record, and every trade, report and
routine tick stays in the history.

Your computer's own clock and timezone make no difference to this.

---

## The app lock

**Settings → Security** sets a numeric passcode, asked for every time the app
opens, plus a security question used to change or recover it.

- The passcode is never stored. A salted SHA-256 of it is.
- Changing the passcode requires answering the security question first.
- Forgot it? **Forgot passcode?** on the lock screen, then the security question.
- The answer ignores capitalisation and surrounding spaces.

**What this is and is not.** It keeps a passing glance out: a laptop left open,
a shared machine, someone walking past. It is **not encryption**. Your entries
sit in the browser's storage in the clear, and anyone with the device and the
know-how can read them without ever seeing the lock screen. If you need more
than that, use full-disk encryption underneath it.

The lock is not part of a backup, deliberately. Importing someone else's file
will not hand over their passcode, and wiping the journal will not quietly
unlock the app.

---

## Reports in Persian

The interface is English. Report and reflection text is not assumed to be — type
in Persian and it lays out right-to-left on its own, per field, using the
browser's own direction detection. English in the same box stays left-to-right.
Nothing to switch on.

---

## What is in this folder

| File | What it does |
| --- | --- |
| `tradepsy.html` | The whole application. |
| `manifest.webmanifest` | Name, icons and window settings for the installed app. |
| `sw.js` | Caches the app so it opens offline. Never touches your journal. |
| `icons/` | App icons, in every size the browser and OS ask for. |
| `serve.py` | The local server. |
| `Start Tradepsy (Windows).bat` | Double-click launcher for Windows. |
| `Start Tradepsy (macOS).command` | Double-click launcher for macOS. |

## Back up sometimes

Browser storage is not permanent. Clearing site data, a "clean up browsing data"
sweep, or reinstalling the browser can take the journal with it.
**Settings → Data & storage → Export data** writes a single JSON file. Keeping a
recent one somewhere else is the only real protection.
