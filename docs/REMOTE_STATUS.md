# Remote status

- Private GitHub repository created: `https://github.com/undefinted/awesome-embodied-diagnostics`
- Local initial commit: `c5b080afa7f250766253b3375391006eb0bc66ba`
- At repository assembly time, GitHub API access worked but three HTTPS Git pushes failed to establish a connection to `github.com:443` after approximately 21 seconds.
- This was a network transport failure, not an authentication, repository-permission or GitHub file-size rejection.

When Git HTTPS connectivity is available, run from either local repository:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\push_when_online.ps1
```

Do not recreate the remote repository; it already exists and is private.
