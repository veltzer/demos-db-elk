# SSH Tunnel Exercise: Reaching Kibana Through an SSH Tunnel

## Overview

This exercise teaches you how to access a Kibana instance that is **not**
directly reachable from your machine, by building an SSH tunnel to the server
it runs on. You will learn how to do this on Linux, macOS, and Windows.

In most real deployments Kibana is **not** exposed to the open internet. It
holds a window into all of your data, and historically it has shipped with no
authentication of its own, so leaving port `5601` open to the world is a
serious mistake. The common, safe pattern is therefore:

- Elasticsearch and Kibana run on a server (or inside a private network /
  VPC).
- Kibana listens only on the server's `localhost` (`127.0.0.1:5601`), so
  nothing outside the server can connect to it directly.
- You already have SSH access to that server (because almost every server you
  administer is reachable over SSH).
- You "borrow" that existing, encrypted SSH connection to carry your Kibana
  traffic. This is called **SSH local port forwarding**, or an **SSH tunnel**.

The key idea to internalize: an SSH tunnel lets a port on **your** machine
behave as if it were a port on the **remote** machine. You point your browser
at `http://localhost:5601` on your laptop, SSH quietly ferries that traffic
over the encrypted connection to the server, and the server delivers it to
Kibana as though the request came from the server itself. No new firewall hole,
no new password, no unencrypted Kibana port on the network — you reuse the trust
and encryption that SSH already provides.

## Prerequisites

- A server running Elasticsearch and Kibana (see
  [`00_install`](../00_install/exercise.md)). This can be a real remote
  machine, a cloud VM, or even a VM / container on your own laptop — anything
  you reach over SSH.
- SSH access to that server: a username, the host's address, and either a
  password or (preferably) an SSH key.
- Kibana listening on the server. For the exercise to be meaningful, Kibana
  should be bound to the server's `localhost` so that the **only** way in is
  through the tunnel.
- An SSH client on your local machine. Linux and macOS ship with `ssh`
  built in; Windows 10/11 include the OpenSSH client, and PuTTY is a popular
  alternative.

## Background: how local port forwarding works

The command you will use everywhere is built from this template:

```
ssh -L <local_port>:<target_host>:<target_port> <user>@<ssh_server>
```

Read the `-L` argument as three colon-separated pieces:

- `<local_port>` — the port opened **on your machine**. You will connect your
  browser here.
- `<target_host>:<target_port>` — where the **SSH server** should forward the
  traffic to, evaluated **from the SSH server's point of view**.

This last point is the single most common source of confusion, so it is worth
slowing down on. After SSH logs into the server, it makes a second connection
**from the server** to `<target_host>:<target_port>`. Because Kibana lives on
the very same server you SSH into, and listens on that server's loopback
address, the target is `localhost:5601` — meaning "localhost as seen by the
server," i.e. the server talking to itself. So the full command is almost
always:

```
ssh -L 5601:localhost:5601 user@server
```

Translated to English: *"open port 5601 on my laptop; anything that arrives
there, send it over this SSH connection and have the server forward it to its
own `localhost:5601`, which is where Kibana is listening."*

A few useful variations on the target:

- `localhost:5601` — Kibana runs on the same host you SSH into (the usual
  case).
- `10.0.0.5:5601` — Kibana runs on a **different** machine that only the SSH
  server can reach. The SSH server acts as a jump host into the private
  network. The forwarding endpoint is still evaluated from the server's
  perspective, which is exactly why this works.

And a note on the local port: it does **not** have to match. If something on
your laptop already uses `5601`, use a different local port:

```
ssh -L 15601:localhost:5601 user@server
```

Then browse to `http://localhost:15601`. Only the left number changes; the
right side still describes Kibana as the server sees it.

---

## Part 1: Linux

On Linux the OpenSSH client is essentially always present. Open a terminal.

### Exercise 1.1: Build the tunnel

```bash
ssh -L 5601:localhost:5601 user@server
```

Replace `user` with your username on the server and `server` with its hostname
or IP address. This drops you into a normal shell on the server **and** keeps
the tunnel open for as long as that SSH session stays alive. Leave this
terminal open.

### Exercise 1.2: Use Kibana

With the tunnel up, open a browser on your laptop and go to:

```
http://localhost:5601
```

You are now looking at the remote Kibana. Confirm it works, then return to the
terminal and press `Ctrl-D` (or type `exit`) to close the session — which also
tears down the tunnel.

### Exercise 1.3: A tunnel without a shell

Often you want the tunnel **only**, without an interactive shell cluttering a
terminal. Add three flags:

```bash
ssh -fNL 5601:localhost:5601 user@server
```

- `-f` — go into the background after authenticating.
- `-N` — do not run a remote command (no shell); just forward ports.
- `-L` — the forwarding rule, as before.

This returns your prompt immediately while the tunnel keeps running in the
background. To find and stop it later:

```bash
ps aux | grep 'ssh -fNL'   # find the process id
kill <pid>                 # stop that tunnel
```

### Exercise 1.4: Keep the tunnel alive

Idle SSH connections can be dropped by firewalls or the server. Ask SSH to send
a small keepalive every 60 seconds so the tunnel survives quiet periods:

```bash
ssh -o ServerAliveInterval=60 -o ServerAliveCountMax=3 \
    -L 5601:localhost:5601 user@server
```

---

## Part 2: macOS

macOS ships with the same OpenSSH client as Linux, so **every command in
Part 1 works identically** in the Terminal app (or iTerm2). There is nothing
extra to install.

### Exercise 2.1: Build the tunnel

Open **Terminal** (Applications → Utilities → Terminal) and run:

```bash
ssh -L 5601:localhost:5601 user@server
```

Then browse to `http://localhost:5601` exactly as on Linux.

### Exercise 2.2: macOS-specific notes

- If you use an SSH key stored in the macOS keychain, add `-A` only if you
  actually need agent forwarding; it is not required for a simple tunnel.
- macOS may warn the first time you connect to a new host
  (`The authenticity of host ... can't be established`). Type `yes` to accept
  and record the host key — this is normal and expected on a first connection.
- The background form (`ssh -fNL ...`) and the keepalive options from Part 1
  behave the same way on macOS.

---

## Part 3: Windows

Windows has two good options. Pick one.

### Exercise 3.1: Built-in OpenSSH (PowerShell or Command Prompt)

Modern Windows 10 and Windows 11 include the same OpenSSH client used on
Linux and macOS. Open **PowerShell** or **Command Prompt** and run the
**identical** command:

```powershell
ssh -L 5601:localhost:5601 user@server
```

Then open a browser and go to `http://localhost:5601`.

If `ssh` is not recognized, enable the optional feature: go to
**Settings → Apps → Optional features → Add a feature**, then install
**OpenSSH Client**. After that the command above will work.

The background tunnel form is slightly different on Windows because `-f` is
less reliable there. The simplest approach is to run the tunnel in its own
window and minimize it:

```powershell
ssh -N -L 5601:localhost:5601 user@server
```

`-N` keeps the connection open for forwarding without opening a remote shell;
leave the window running and minimized while you use Kibana.

### Exercise 3.2: PuTTY (graphical alternative)

If you prefer a GUI, or are on an older Windows that lacks the OpenSSH client,
use **PuTTY** (download from <https://www.putty.org>). PuTTY configures the
exact same kind of tunnel through dialog boxes instead of command-line flags:

1. Launch PuTTY.
1. In the **Session** category, enter the server's hostname or IP in
   **Host Name** and leave the port at `22`.
1. In the left-hand tree, expand **Connection → SSH → Tunnels**.
1. In **Source port**, type `5601` (the port opened on your Windows machine).
1. In **Destination**, type `localhost:5601` (where the server should forward
   to — evaluated from the server's perspective, just like the `-L` command).
1. Make sure **Local** and **Auto** are selected, then click **Add**. You
   should see `L5601  localhost:5601` appear in the list of forwarded ports.
1. Go back to the **Session** category, optionally type a name under
   **Saved Sessions** and click **Save** so you can reuse this configuration.
1. Click **Open**, then log in with your username and password (or key).

Leave the PuTTY window open and browse to `http://localhost:5601`. Closing the
PuTTY window closes the tunnel.

---

## Part 4: Verification and troubleshooting

### Exercise 4.1: Confirm the tunnel is actually carrying traffic

With a tunnel up, this should return Kibana's HTML or a redirect, proving the
local port is wired through to the remote Kibana:

```bash
curl -I http://localhost:5601
```

On Windows PowerShell, the equivalent is:

```powershell
curl.exe -I http://localhost:5601
```

### Exercise 4.2: Common problems

- **`Connection refused` in the browser, but SSH logged in fine.** The SSH
  side is working; the *target* side is not. Kibana probably is not running, or
  is listening on a different port/address on the server. SSH into the server
  and check `curl -I http://localhost:5601` **on the server itself**.
- **`channel ... open failed: connect failed`** in the SSH output. SSH reached
  the server but the server could not connect onward to
  `<target_host>:<target_port>`. Re-check that piece — it is evaluated from the
  *server's* point of view, not yours.
- **`bind: Address already in use`** when starting the tunnel. Your chosen
  local port is taken. Pick another, e.g. `-L 15601:localhost:5601`, and browse
  to `http://localhost:15601`.
- **The tunnel drops after a few minutes of inactivity.** Add the keepalive
  options from Exercise 1.4.
- **Kibana loads but assets look broken / it redirects oddly.** Some Kibana
  configurations set a `server.publicBaseUrl`. If so, match your local port to
  the remote port (use `5601:localhost:5601`, not a remapped local port) so the
  URLs line up.

### Exercise 4.3: Reason about security

Answer these for yourself to confirm you understood the model:

1. Why is an SSH tunnel safer than simply opening port `5601` on the server's
   firewall?
1. The traffic between your browser and the server is encrypted by SSH. Is the
   traffic between the **server** and Kibana also encrypted? Why is that
   usually acceptable?
1. If Kibana were on a *different* machine inside the private network, what
   would the `-L` target become, and from whose perspective is that address
   resolved?

## Expected Deliverables

1. A screenshot of Kibana loaded at `http://localhost:5601` on your local
   machine through the tunnel.
1. The exact `ssh -L` command (or PuTTY tunnel configuration) you used.
1. Written answers to the three questions in Exercise 4.3.

## Tips for Success

- Start with the same-host case (`localhost:5601`) before attempting a jump
  host into a private network.
- Keep the local and remote ports identical unless you have a reason not to;
  it removes a whole class of confusion.
- Remember the asymmetry: the **left** side of `-L` is your machine, the
  **right** side is resolved from the server.
- Use `-N` (no shell) for a clean, dedicated tunnel; use `-f` (Linux/macOS) to
  push it into the background.

## Further Reading

- [OpenSSH `ssh(1)` manual — `-L` port forwarding](https://man.openbsd.org/ssh#L)
- [PuTTY documentation — port forwarding](https://the.earth.li/~sgtatham/putty/0.81/htmldoc/Chapter3.html#using-port-forwarding)
- [Kibana settings — `server.host` and `server.publicBaseUrl`](https://www.elastic.co/guide/en/kibana/current/settings.html)
